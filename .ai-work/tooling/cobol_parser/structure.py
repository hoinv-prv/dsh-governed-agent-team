"""Structure parse — 部・節・段落・完結文 (文法書 2.7.3, 2.7.4).

SHALLOW by design (P2 of AIP-EXEC-048): the tree goes down to statements split
at known verbs; the per-verb 書き方 parsing is the P3 registry's job. A sentence
whose leading content is not a known verb becomes ONE RawStatement (verb "") —
never an error, so a whole file always parses.

Anchoring: headers are recognized only at tokens that are the FIRST significant
token of their line AND start in area A (content bytes 0-3) — exactly the
reference's margin-A rule, which is what makes this parse robust.

Statement verbs below are the COBOL85 + ASP set assembled from 付録F 書き方一覧
(SRC-ASP-04-asp-cobol-g-v13-0a47-ph-l-c-f-0665); P3 refines per-verb grammar
from the same appendix.
"""
from __future__ import annotations

from dataclasses import dataclass, field

_DIV_NAMES = ("IDENTIFICATION", "ENVIRONMENT", "DATA", "PROCEDURE")
#: `ID DIVISION.` — written by 5 corpus files (CBNEDIT.CB · DAIYASET.CB ·
#: HA100CB.CB · MINSTSET.CB · SI0300CB.PRC).
#:
#: It was recorded here as an undocumented vendor form, because ASP COBOL G's
#: 文法書 §3.3.2.1 gives only `IDENTIFICATION DIVISION.` and `ID` is absent from
#: its 予約語表. That was the wrong dialect to look in. ASP JIS COBOL E 文法書
#: §3.2.2 puts `ID DIVISION.` in the 見出し部 format itself, shaded — a Fujitsu
#: extension to JIS COBOL E — and §3.2.2(3)a states the rule outright: the
#: abbreviated form followed by a period and a space may stand in for the
#: standard header. (Read by eye from the scan, pdf 69 = printed 58; the
#: markdown of that manual is damaged OCR and cannot be cited.)
#:
#: So this is not a mystery spelling: it is a DIALECT MARKER, alongside COMP-3
#: (792 files), NOMINAL KEY (139) and ACTUAL KEY (9). The caution stays — the
#: deviation from COBOL G is still worth seeing — but it now names the source.
_DIV_ALIASES = {"ID": "IDENTIFICATION"}

#: Statement verbs (付録F). EXEC absorbs through END-EXEC (SQL etc.).
VERBS = frozenset((
    "ACCEPT", "ADD", "ALTER", "CALL", "CANCEL", "CLOSE", "COMMIT", "COMPUTE",
    "CONTINUE", "COPY", "DELETE", "DISPLAY", "DIVIDE", "EVALUATE", "EXEC",
    "EXIT", "GO", "GOBACK", "IF", "INITIALIZE", "INSPECT", "MERGE", "MOVE",
    "MULTIPLY", "OPEN", "PERFORM", "READ", "RELEASE", "RETURN", "REWRITE",
    "ROLLBACK", "SEARCH", "SET", "SORT", "START", "STOP", "STRING", "SUBTRACT",
    "UNLOCK", "UNSTRING", "WRITE",
    # Legacy / ASP verbs measured in the corpus histogram (P3, AIP-EXEC-048):
    # READY|RESET TRACE · EXAMINE (pre-INSPECT) · LOCK UP · EXHIBIT NAMED ·
    # ENTRY (alternate entry point, a CALL target).
    "READY", "RESET", "EXAMINE", "LOCK", "EXHIBIT", "ENTRY",
))

#: `_VERBS_NOT_IN_RESERVED_TABLE = frozenset(("EXAMINE", "EXHIBIT"))` lived here.
#: It exempted two verbs 付録E of COBOL G does not list, so the splitter would not
#: leave them glued to the statement before (`MOVE SPACE TO A EXAMINE B REPLACING
#: …` typed `REPLACING` and `BY` as MOVE targets). Both are reserved words of JIS
#: COBOL E, and once RESERVED_WORDS became the union of the two dialects the
#: exemption could no longer decide anything: `tok.reserved` was already true for
#: the only two members. Removed rather than left as a comforting no-op — a
#: condition that cannot fire still has to be read and reasoned about by whoever
#: comes next. The patch was measured, not assumed: whole-corpus parse shape is
#: byte-identical without it.

#: A verb spelling that ALSO appears as a clause word inside another statement,
#: mapped to the word that must follow it for it to be a verb. `LOCK` is the ASP
#: verb `LOCK UP file` (85 statements over 33 files, and all 85 spell UP — there
#: is no bare LOCK in the corpus); it is also the option in `CLOSE f WITH LOCK`
#: (付録F §F.10). Without the lookahead the splitter closes the CLOSE early and
#: invents a `LOCK` statement out of its option.
_VERBS_NEEDING_NEXT = {"LOCK": frozenset(("UP",))}


def _heads_a_statement(word: str, toks, idx: int) -> bool:
    """Does this verb spelling actually open a statement here?"""
    need = _VERBS_NEEDING_NEXT.get(word)
    if need is None:
        return True
    for nxt in toks[idx + 1:]:
        if nxt.type in ("SPACE", "COMMENT"):
            continue
        return nxt.type == "WORD" and nxt.text.upper() in need
    return False


#: Branch keywords that close the statement before them: the code after `ELSE`
#: or `WHEN` belongs to a different arm, never to the preceding statement.
_BRANCH_KEYWORDS = frozenset(("ELSE", "WHEN"))

#: I/O condition clauses, optionally preceded by `NOT`. They belong to the I/O
#: statement that opened them, so they close a statement only when the one being
#: collected is NOT that I/O statement — `READ F AT END GO TO X` keeps its own
#: clause; a MOVE inside the arm does not. `KEY` is optional after `INVALID`:
#: KTORIMNT.COB writes `INVALID` and `NOT INVALID` bare.
#: 付録F §F.10 gives the same shape to the arithmetic and string verbs: `ON SIZE
#: ERROR` / `ON OVERFLOW` / `ON EXCEPTION`, each optionally negated, and `AT
#: END-OF-PAGE` (abbreviated `EOP`) on WRITE. Measured before being added:
#: ON SIZE ERROR 40 over 9 files, AT EOP 8 over 5; ON OVERFLOW, ON EXCEPTION and
#: the spelled-out AT END-OF-PAGE do not occur here but are named by the book.
_IO_CLAUSES = (
    ["AT", "END"], ["INVALID", "KEY"], ["INVALID"],
    ["ON", "SIZE", "ERROR"], ["ON", "OVERFLOW"], ["ON", "EXCEPTION"],
    ["AT", "END-OF-PAGE"], ["AT", "EOP"],
)
#: Verbs that OWN their condition clause, so the clause is not cut off them.
#: `SEARCH` belongs here for the same reason as READ: §3.6.22.2 prints
#: `SEARCH 一意名-1 [VARYING …] [AT END 無条件文-1] WHEN 条件-1 …`, so the AT END
#: is the statement's own clause. It was missing, so `AT` cut the statement and
#: the arm became an ownerless `AT END` on 13 of the corpus's 17 SEARCHes — the
#: branch taken when the table lookup FAILS, absent from every one of them.
_IO_VERBS = frozenset((
    "READ", "WRITE", "REWRITE", "DELETE", "START", "RETURN", "SEARCH",
    "ADD", "SUBTRACT", "MULTIPLY", "DIVIDE", "COMPUTE", "STRING", "UNSTRING", "CALL",
))
#: Sentinel for "a clause was just opened here" — keeps `NOT AT END` one clause
#: instead of splitting again at the `AT`.
_IO_CLAUSE_OPEN = "\x00io-clause"

_LEVEL_INDICATORS = ("FD", "SD")
#: 2.7.4: level numbers are 01-49, 66, 77, 88.
_LEVEL_NUMBERS = frozenset([f"{n:02d}" for n in range(1, 50)] + ["66", "77", "88"])

#: Compiler-directing words written standalone with NO period (corpus reality,
#: e.g. PL1820CB.PRC) — a sentence made only of these closes at the line break.
_DIRECTIVES = frozenset(("SKIP1", "SKIP2", "SKIP3", "EJECT"))
#: Directive sentences that DO carry a period: `ENDCOBOL.` (ASP terminator),
#: `END PROGRAM <name>.` / `END COBOL.`, and a stray `END-COPY.` left after a
#: COPY that already closed with its own period (JH230CB.PRC:1488).
_DIRECTIVE_HEADS = frozenset(("ENDCOBOL", "END", "END-COPY"))

#: Divisions whose sentences are declarative clauses, not procedure statements.
_CLAUSE_DIVISIONS = frozenset(("IDENTIFICATION", "ENVIRONMENT"))


@dataclass
class Statement:
    verb: str  # "" = RawStatement
    tokens: list
    line_no: int
    #: Statements this one contains — the THEN arm of an IF, an inline PERFORM's
    #: loop body, the statements under a WHEN or an AT END. Empty unless `tree()`
    #: built the shape.
    body: list = field(default_factory=list)
    #: The ELSE arm of an IF.
    else_body: list = field(default_factory=list)
    #: Alternatives that carry their own body: WHEN … of an EVALUATE/SEARCH, and
    #: the AT END / INVALID KEY arms of an I/O statement. Each is itself a
    #: Statement whose `body` holds the arm.
    branches: list = field(default_factory=list)

    @property
    def parsed(self):
        """Typed clauses for this verb, or None when no parser is registered.

        Lazy on purpose: most callers only look at a few statements, and typing
        700k of them to answer one question would be pure cost.
        """
        if not hasattr(self, "_parsed"):
            from .registry import parse_statement  # local: keeps the layer one-way

            self._parsed = parse_statement(self)
        return self._parsed


def classify_sentence(tokens: list, division: str, debug_lines: set | None = None) -> str:
    """data_entry | directive | clause | statements | raw — decided before
    anything reads the sentence as procedure code (P3, AIP-EXEC-048).

    Order matters: a data entry is recognized by its LEVEL, not by its division,
    because a copybook carries data entries with no division header at all.
    """
    if not tokens:
        return "raw"
    head = tokens[0]
    # A sentence written entirely on `D` lines is debug-only code (compiled just
    # WITH DEBUGGING MODE); this corpus also parks commented-out banners there.
    if debug_lines and all(
        all(seg[0] in debug_lines for seg in t.segments) for t in tokens if t.segments
    ):
        return "debug"
    up = head.text.upper() if head.type == "WORD" else ""
    if up in _LEVEL_INDICATORS:
        return "data_entry"
    if head.type == "NUMBER" and head.text.lstrip("0").isdigit() or head.text == "0":
        if head.text.zfill(2) in _LEVEL_NUMBERS and len(head.text) <= 2:
            return "data_entry"
    if up in _DIRECTIVES or up in _DIRECTIVE_HEADS:
        return "directive"
    if division in _CLAUSE_DIVISIONS:
        return "clause"
    if up in VERBS and head.reserved:
        return "statements"
    if division == "DATA":
        return "data_entry"  # continuation clauses of an entry
    # A RESERVED non-verb head is a clause of an entry the sentence started in —
    # a copybook may begin mid-entry (`BLOCK CONTAINS 12 RECORDS …`). An unknown
    # USER word stays raw, so the coverage metric keeps meaning what it says.
    if head.reserved:
        return "clause"
    return "raw"


@dataclass
class Sentence:
    tokens: list
    line_no: int
    kind: str = "statements"

    @property
    def parsed(self):
        """Typed clauses for a sentence that is not a statement — today, SELECT.

        Symmetric with `Statement.parsed`, and lazy for the same reason: a scan
        touches every sentence and types almost none of them.
        """
        if not hasattr(self, "_parsed_clause"):
            from .registry import parse_clause  # local: keeps the layer one-way

            self._parsed_clause = parse_clause(self)
        return self._parsed_clause

    def tree(self) -> list[Statement]:
        """The statements of this sentence, SHAPED — arms nested inside the
        statement that owns them.

        `split_statements()` stays flat because extraction and the coverage
        metric want every statement in reading order; this answers the other
        question: what runs when this condition holds.

        Two things make it more than a bracket match. A scope usually has NO
        terminator — 71% of the corpus's IFs are closed by the sentence's period
        — so every open scope closes at the end. And `ELSE` binds to the nearest
        IF that has not taken one yet, which is what makes an unterminated
        nested IF read correctly.
        """
        roots: list[Statement] = []
        # stack entries: (owner statement, the list its children go into)
        stack: list[tuple[Statement, list]] = []

        def sink() -> list:
            return stack[-1][1] if stack else roots

        for st in self.split_statements():
            verb = st.verb

            if verb.startswith("END-") and verb != "END-EXEC":
                # close the innermost scope this terminator can close
                for depth in range(len(stack) - 1, -1, -1):
                    if _SCOPES.get(stack[depth][0].verb) == verb:
                        del stack[depth:]
                        break
                continue

            if verb == "ELSE":
                # bind to the nearest IF that has not taken an ELSE yet
                for depth in range(len(stack) - 1, -1, -1):
                    owner = stack[depth][0]
                    if owner.verb == "IF" and not owner.else_body:
                        del stack[depth + 1 :]
                        owner.else_body = []
                        stack[depth] = (owner, owner.else_body)
                        break
                continue

            if verb in _ARM_MARKERS:
                # WHEN / AT END / INVALID KEY open an arm of the nearest scope
                for depth in range(len(stack) - 1, -1, -1):
                    owner = stack[depth][0]
                    if owner.verb in _SCOPES:
                        del stack[depth + 1 :]
                        owner.branches.append(st)
                        stack.append((st, st.body))
                        break
                else:
                    sink().append(st)
                continue

            sink().append(st)
            if verb in _SCOPES:
                # Some scopes have to prove they opened a body: an out-of-line PERFORM
                # has none, and `ADD A TO B` followed by another statement in the same
                # sentence has none either. The proof is a terminator somewhere in the
                # sentence, or a condition clause on the statement itself.
                if verb in _SCOPES_NEEDING_PROOF and not (
                    self._has_terminator(_SCOPES[verb]) or _opens_a_condition_arm(st)
                ):
                    continue
                stack.append((st, st.body))

        return roots

    def _has_terminator(self, terminator: str) -> bool:
        return any(s.verb == terminator for s in self.split_statements())

    def split_statements(self) -> list[Statement]:
        """The sentence's statements, flat and in reading order.

        Computed once and kept: `tree()` shapes THESE objects, so typing a
        statement through either view is visible in the other, and identity is
        a usable answer to "did nesting lose anything?".
        """
        if not hasattr(self, "_statements"):
            self._statements = self._split()
        return self._statements

    def _split(self) -> list[Statement]:
        """Cut the sentence into statements.

        A statement ends at the next VERB — and also at anything that begins a
        different part of an enclosing statement, or the split silently hands
        those words to the statement before them. Measured on the corpus before
        this was handled: 16666 MOVEs whose "target" was `END-IF`, 14499 `ELSE`,
        7816 `WHEN`.
        """
        out: list[Statement] = []
        cur: list = []
        absorb_exec = False
        open_verb = ""  # the verb of the statement currently being collected

        def close():
            nonlocal cur
            if cur:
                out.append(_mk_statement(cur))
            cur = []

        toks = self.tokens
        for idx, tok in enumerate(toks):
            word = tok.text.upper() if tok.type == "WORD" else ""
            if absorb_exec:
                cur.append(tok)
                if word == "END-EXEC":
                    absorb_exec = False
                continue

            if word in VERBS and tok.reserved and _heads_a_statement(word, toks, idx):
                close()
                cur = [tok]
                open_verb = word
                absorb_exec = word == "EXEC"
                continue

            # `END-IF`, `END-READ`, … close whatever they terminate
            if tok.reserved and word.startswith("END-") and word != "END-EXEC":
                close()
                out.append(_mk_statement([tok]))
                open_verb = ""
                continue

            # `ELSE` / `WHEN` open another arm, and carry its selector with them
            if tok.reserved and word in _BRANCH_KEYWORDS:
                close()
                cur = [tok]
                open_verb = word
                continue

            # `AT END` / `INVALID KEY`, optionally preceded by `NOT`, belong to
            # an I/O statement. Split only when the statement being collected is
            # NOT that I/O statement — `READ F AT END …` keeps its own clause.
            # `cur` is deliberately NOT required. When the previous arm's body
            # ends with `END-IF`, everything is already closed and the marker
            # opens a fresh statement with nothing collected — this branch used
            # to be skipped there, `open_verb` stayed empty, and the following
            # `INVALID` split again, leaving a bare `NOT` and an ownerless
            # `INVALID KEY` (CMB010CG.COB:662; 6 statements over 3 files).
            # ELSE and WHEN never reach here: `_BRANCH_KEYWORDS` above consumes
            # them, which is why relaxing this touches 6 statements and not the
            # 3449 other markers that follow an END-*.
            if tok.reserved and open_verb not in _IO_VERBS and open_verb != _IO_CLAUSE_OPEN:
                # The window has to hold the longest clause plus a leading NOT:
                # `NOT ON SIZE ERROR` is four words, and a 2-token lookahead could
                # never match the three-word clauses at all.
                rest = [tok] + [t for t in toks[idx + 1 : idx + 4]]
                heads = [t.text.upper() for t in rest if t.type == "WORD"]
                negated = heads[:1] == ["NOT"]
                if negated:
                    heads = heads[1:]
                # `NOT END` (PZ0015CG.COB:100) drops the AT; a bare `END` only
                # counts as the clause when NOT introduced it, since `END` alone
                # appears far too often to treat as a boundary.
                if (heads[:3] in _IO_CLAUSES or heads[:2] in _IO_CLAUSES
                        or heads[:1] in _IO_CLAUSES or (negated and heads[:1] == ["END"])):
                    if cur:
                        close()
                    # `NOT AT END` is ONE clause: having just cut here, do not
                    # cut again at the `AT` that follows. With nothing collected
                    # there is no cut to make, but the clause is open all the
                    # same and the mark still has to be set.
                    open_verb = _IO_CLAUSE_OPEN

            cur.append(tok)
        close()
        return out


#: Words that head a statement only because the splitter cut there: a branch
#: keyword, or the start of an I/O condition clause. They are recognized rather
#: than left as RawStatements — the parser knows exactly what they are, and
#: calling them unrecognized would understate coverage.
_MARKER_VERBS = _BRANCH_KEYWORDS | frozenset(("AT", "INVALID", "NOT"))

#: Verbs whose scope holds other statements, with the terminator that closes it.
#: Absent a terminator the scope runs to the end of the sentence — the majority
#: form here: 14075 IFs in the corpus, only 4882 END-IFs.
_SCOPES = {
    "IF": "END-IF",
    "EVALUATE": "END-EVALUATE",
    "SEARCH": "END-SEARCH",
    "PERFORM": "END-PERFORM",  # inline only; an out-of-line PERFORM has no body
    "READ": "END-READ",
    "WRITE": "END-WRITE",
    "REWRITE": "END-REWRITE",
    "DELETE": "END-DELETE",
    "START": "END-START",
    "RETURN": "END-RETURN",
    # 付録F §F.10 names a terminator for these too. Measured on this corpus:
    # DIVIDE 243 over 106 files, CALL 94/47, STRING 44/26, COMPUTE 27/10,
    # MULTIPLY 2/2; ADD, SUBTRACT and UNSTRING never appear with one, and are
    # modelled anyway because the book gives them one.
    "ADD": "END-ADD",
    "SUBTRACT": "END-SUBTRACT",
    "MULTIPLY": "END-MULTIPLY",
    "DIVIDE": "END-DIVIDE",
    "COMPUTE": "END-COMPUTE",
    "STRING": "END-STRING",
    "UNSTRING": "END-UNSTRING",
    "CALL": "END-CALL",
}
#: Scopes that must PROVE they opened a body. `ADD A TO B  MOVE 1 TO C.` is two
#: statements in one sentence, so an ADD that opened a scope unconditionally would
#: swallow the MOVE. An I-O verb is left out of this: its behaviour is pinned by the
#: existing tests and by a corpus scorecard, and widening the rule there would be a
#: change to measured output rather than a fix.
_SCOPES_NEEDING_PROOF = frozenset((
    "PERFORM", "ADD", "SUBTRACT", "MULTIPLY", "DIVIDE", "COMPUTE",
    "STRING", "UNSTRING", "CALL",
))
#: Markers that open an alternative inside a scope rather than closing it.
#:
#: `ON` is deliberately NOT here, and that is a measurement rather than an
#: oversight. It was added with the arithmetic scopes on the assumption that
#: `ON SIZE ERROR` needs to open an arm — but the splitter only cuts at a
#: condition clause when the statement being collected is NOT the one that owns
#: it, and every verb that can carry `ON SIZE ERROR` / `ON OVERFLOW` /
#: `ON EXCEPTION` is in `_IO_VERBS`. So `ON` never starts a statement: 0 in
#: 10616 files, and the mutation check could not make its absence fail. Adding
#: it back needs a case that reaches it first.
_ARM_MARKERS = frozenset(("WHEN", "AT", "INVALID", "NOT"))


def _opens_a_condition_arm(st) -> bool:
    """Does this statement carry its own condition clause?

    A verb in `_IO_VERBS` keeps its clause rather than having it cut off, so
    `DIVIDE … ON SIZE ERROR` ends with the clause words and the arm's body follows
    as separate statements. That trailing clause is the evidence that a body was
    opened at all, which `ADD A TO B` does not have.
    """
    words = [t.text.upper() for t in st.tokens if t.type == "WORD"]
    return any(words[i:i + len(c)] == c for c in _IO_CLAUSES for i in range(len(words)))


def _mk_statement(tokens: list) -> Statement:
    head = tokens[0]
    upper = head.text.upper() if head.type == "WORD" else ""
    verb = ""
    if upper in VERBS or (head.reserved and (upper in _MARKER_VERBS or upper.startswith("END-"))):
        verb = upper
    return Statement(verb=verb, tokens=tokens, line_no=head.segments[0][0] if head.segments else 0)


@dataclass
class DataEntry:
    level: str  # FD | SD | 01..49 | 66 | 77 | 88
    name: str
    tokens: list

    @property
    def parsed(self):
        """Typed clauses — 付録F §F.6 for FD/SD, §F.7 for a level entry.

        Lazy, and here that is not a nicety: this corpus holds 511495 data entries
        and a caller usually wants a handful.
        """
        if not hasattr(self, "_parsed_entry"):
            from .registry import parse_entry  # local: keeps the layer one-way

            self._parsed_entry = parse_entry(self)
        return self._parsed_entry


@dataclass
class Paragraph:
    name: str
    sentences: list = field(default_factory=list)


@dataclass
class Section:
    name: str  # "" = implicit
    paragraphs: list = field(default_factory=list)


@dataclass
class Division:
    name: str  # "" = prelude (copybooks have no division headers)
    sections: list = field(default_factory=list)

    def sentences(self):
        return [s for sec in self.sections for p in sec.paragraphs for s in p.sentences]

    #: Sentence kinds that carry executable statements. `debug` is included: a
    #: `D` line is conditionally compiled, NOT commented out, and this corpus
    #: calls real programs from one — excluding it lost 4 true call edges.
    STATEMENT_KINDS = ("statements", "raw", "debug")

    def statements(self, kinds: tuple = STATEMENT_KINDS):
        """Statements of the procedural sentences — a data entry or a compiler
        directive is not an unrecognized statement."""
        return [st for s in self.sentences() if s.kind in kinds for st in s.split_statements()]

    def compiler_directing(self, verb: str = "COPY"):
        """Compiler-directing statements wherever they sit — including INSIDE a
        data entry, which is how 9 corpus files pull a record in
        (`01 AREC COPY ATRKJNR.`). Procedural `statements()` cannot see those.
        """
        out = []
        for s in self.sentences():
            if s.kind in self.STATEMENT_KINDS:
                continue
            for st in s.split_statements():
                if st.verb == verb:
                    out.append(st)
        return out

    def entries(self):
        out = []
        for sent in self.sentences():
            toks = sent.tokens
            if not toks:
                continue
            head = toks[0]
            level = ""
            if head.type == "WORD" and head.text.upper() in _LEVEL_INDICATORS:
                level = head.text.upper()
            elif head.type == "NUMBER" and len(head.text) <= 2 and head.text.isdigit():
                level = head.text.zfill(2)
            if not level:
                continue
            # The name is the next WORD, not the next TOKEN: COPYLIB writes
            # `06 / WS-AR REDEFINES / WS-A`, and taking position 1 made the name
            # `/`. Scan past separators instead of trusting the slot.
            name = ""
            for tok in toks[1:4]:
                if tok.type == "WORD":
                    name = tok.text.upper()
                    break
                if tok.type in ("NUMBER", "STRING"):
                    break
            out.append(DataEntry(level=level, name=name, tokens=toks))
        return out


@dataclass
class Program:
    divisions: list = field(default_factory=list)
    program_id: str = ""
    cautions: list = field(default_factory=list)

    def division(self, name: str) -> Division:
        for d in self.divisions:
            if d.name == name.upper():
                return d
        return Division(name=name.upper())


def parse_program(lines, tokens) -> Program:
    sig = [t for t in tokens if t.type not in ("SPACE", "COMMENT", "COMMENT_ENTRY") and t.segments]
    debug_lines = {ln.line_no for ln in lines if ln.kind == "debug"}

    # first significant token of each line (by the token's FIRST segment)
    first_on_line: dict[int, int] = {}
    for idx, tok in enumerate(sig):
        no = tok.segments[0][0]
        first_on_line.setdefault(no, idx)

    def is_line_head(idx: int) -> bool:
        tok = sig[idx]
        no, start, _ = tok.segments[0]
        return first_on_line.get(no) == idx and start < 4

    prog = Program()
    div = Division(name="")
    sec = Section(name="")
    par = Paragraph(name="")

    def flush_paragraph():
        nonlocal par
        if par.sentences or par.name:
            sec.paragraphs.append(par)
        par = Paragraph(name="")

    def flush_section():
        nonlocal sec
        flush_paragraph()
        if sec.paragraphs or sec.name:
            div.sections.append(sec)
        sec = Section(name="")

    def flush_division():
        nonlocal div
        flush_section()
        if div.sections or div.name:
            prog.divisions.append(div)
        div = Division(name="")

    n = len(sig)

    def header_kind(idx: int) -> str:
        """'' | 'division' | 'section' | 'paragraph' — header anchored at idx."""
        tok = sig[idx]
        if not (is_line_head(idx) and tok.type == "WORD"):
            return ""
        nxt = sig[idx + 1] if idx + 1 < n else None
        upper = tok.text.upper()
        if (
            (upper in _DIV_NAMES or upper in _DIV_ALIASES)
            and nxt is not None
            and nxt.type == "WORD"
            and nxt.text.upper() == "DIVISION"
        ):
            return "division"
        if nxt is not None and nxt.type == "WORD" and nxt.text.upper() == "SECTION":
            return "section"
        # a data entry never has its period right after the area-A word
        if div.name != "DATA" and nxt is not None and nxt.type == "SEP" and nxt.text == ".":
            return "paragraph"
        return ""

    i = 0
    while i < n:
        tok = sig[i]
        kind = header_kind(i)
        if kind == "division":
            flush_division()
            name = tok.text.upper()
            if name in _DIV_ALIASES:
                prog.cautions.append(
                    f"line {tok.segments[0][0]}: `{name} DIVISION` — JIS COBOL E "
                    f"form (E 文法書 §3.2.2, Fujitsu extension); ASP COBOL G "
                    f"文法書 §3.3.2.1 documents only `{_DIV_ALIASES[name]} DIVISION`"
                )
                name = _DIV_ALIASES[name]
            div = Division(name=name)
            while i < n and not (sig[i].type == "SEP" and sig[i].text == "."):
                i += 1
            i += 1
            continue
        if kind == "section":
            flush_section()
            sec = Section(name=tok.text.upper())
            while i < n and not (sig[i].type == "SEP" and sig[i].text == "."):
                i += 1
            i += 1
            continue
        if kind == "paragraph":
            flush_paragraph()
            par = Paragraph(name=tok.text.upper())
            i += 2
            continue

        # sentence: accumulate to the separator period — BUT stop short of a new
        # area-A header, so a period-less directive (SKIP2, EJECT…) or a missing
        # period cannot swallow the next division/section/paragraph
        sent_tokens = []
        line_no = tok.segments[0][0]
        while i < n:
            if sent_tokens and header_kind(i):
                break
            t = sig[i]
            # `D` lines are compiled only WITH DEBUGGING MODE. That governs the
            # PERIOD — ordinary code cannot depend on a debug line to finish its
            # sentence, and debug lines here often omit the period entirely — but
            # it does NOT split the sentence. `IF c / D DISPLAY / MOVE …` is one
            # sentence in both compile modes, and breaking there cost the IF BOTH
            # arms: every guarded statement came out a top-level sibling, i.e.
            # unconditional. 369 corpus sentences over 22 files are cut by a D
            # line, 56 of them IFs over 11 files.
            #
            # The half worth keeping is the other direction: a sentence that
            # STARTS on a debug line must not swallow the ordinary code after it.
            tok_debug = bool(t.segments) and t.segments[0][0] in debug_lines
            start_debug = (
                bool(sent_tokens)
                and bool(sent_tokens[0].segments)
                and sent_tokens[0].segments[0][0] in debug_lines
            )
            if sent_tokens and start_debug and not tok_debug:
                break
            # a directive-only sentence (SKIP2, EJECT…) has no period: it closes
            # at the line break instead of swallowing the next line's content
            if (
                sent_tokens
                and t.segments
                and t.segments[0][0] != sent_tokens[-1].segments[-1][0]
                and all(x.type == "WORD" and x.text.upper() in _DIRECTIVES for x in sent_tokens)
            ):
                break
            sent_tokens.append(t)
            i += 1
            # A period ON a debug line cannot close a sentence that began in
            # ordinary code: that period is absent whenever DEBUGGING MODE is off,
            # so the sentence it appears to end would run on without it.
            if t.type == "SEP" and t.text == "." and not (tok_debug and not start_debug):
                break
        body = (
            sent_tokens[:-1]
            if sent_tokens and sent_tokens[-1].type == "SEP" and sent_tokens[-1].text == "."
            else sent_tokens
        )
        sentence = Sentence(
            tokens=body, line_no=line_no, kind=classify_sentence(body, div.name, debug_lines)
        )
        par.sentences.append(sentence)

        # PROGRAM-ID paragraph: its first sentence names the program
        if par.name == "PROGRAM-ID" and not prog.program_id and sentence.tokens:
            head = sentence.tokens[0]
            if head.type in ("WORD", "NUMBER"):
                prog.program_id = head.text.upper()

    flush_division()
    return prog
