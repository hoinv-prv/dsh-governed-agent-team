"""Per-verb clause typing — 第3章 書き方 / 付録F.

P2 recognized a statement by its verb; this reads its CLAUSES, so a consumer can
ask what a MOVE writes to, or which paragraphs a PERFORM runs, without going back
to the tokens.

Scope: statements with no nested body. IF / EVALUATE / SEARCH and inline PERFORM
contain other statements, which needs the splitter to nest — a separate change,
measured on its own. A verb with no parser here keeps `parsed = None`, so nothing
regresses and `run_coverage.py` reports the share that is typed.

Names are recorded as their HEAD word: `WS-A OF WS-REC` and `WS-TBL (WS-I)` are
one operand each. Qualification and subscripts are reference detail, and flatten
what a consumer usually wants — which item, not which occurrence.
"""
from __future__ import annotations

from dataclasses import dataclass, field

#: Separator characters (書き方 punctuation). Only ever ignored as SEP tokens —
#: `MOVE "," TO …` is a real literal, and dropping it left 764 corpus statements
#: with no source at all.
_NOISE = {",", ";", "."}


@dataclass
class Write:
    """A typed WRITE — the union of five 書き方 across both dialects.

    G 文法書 §4.4.7.2 (sequential) · §5.4.9.2 (relative) · §6.4.9.2 (indexed)
    E 文法書 §5.4.8 書き方1/2 · §10.4.5 (communication)

    `advancing` and `positioning` are kept apart on purpose. They look alike and
    mean different things: ADVANCING moves the paper, POSITIONING consumes the
    record's first byte as a carriage-control character (E §5.4.8 一般規則). A
    field that merged them would read back as "line feed" for 660 statements
    that actually shorten the record.

    `record_format` holds a DATA NAME whose runtime value selects the record
    layout (G §6.4.9.2, 網掛け — a Fujitsu extension). Same caution as the SELECT
    clause of the same name: it is never a layout name itself.
    """

    record_name: str = ""
    from_operand: str | None = None
    #: "BEFORE" | "AFTER" | None
    advancing: str | None = None
    #: 一意名-2 / 整数-1 / "PAGE"
    advancing_operand: str | None = None
    positioning: str | None = None
    record_format: str | None = None


@dataclass
class If:
    """A typed IF. G 文法書 §3.6.19 · 付録F §F.10 · E 文法書 付録4.

    96869 statements over 2657 files — after MOVE, the most common thing in this
    corpus. The nesting tree already carried the ARMS (`body` / `else_body`);
    what had nowhere to live was the CONDITION, which is what a consumer needs to
    know when the arms run at all.

    `has_then`: `THEN` is a 補助語 and 317 of the 96869 write it. Left inside the
    condition it would read as an operand.

    `then_next_sentence`: 1593 statements close the THEN arm with `NEXT
    SENTENCE`, and in every one of the 1593 it is the LAST token of the IF and
    the statement also has an ELSE — the idiom `IF c NEXT SENTENCE ELSE <work>`,
    i.e. "do the work when NOT c". Reading only `body == []` gives "the true case
    does nothing", which is close enough to be dangerous: NEXT SENTENCE skips the
    rest of the SENTENCE, not just the IF.

    KNOWN LIMIT — `ELSE NEXT SENTENCE` (付録F §F.10, 0 occurrences here) is not
    represented: its tokens reach neither this record nor `else_body`, so it
    currently reads the same as having no ELSE. Named in a test rather than left
    to be discovered.
    """

    condition: str = ""
    #: The data names the condition READS — head words, literals and figurative
    #: constants excluded. `condition` keeps the text; this answers dataflow.
    condition_operands: list = field(default_factory=list)
    has_then: bool = False
    then_next_sentence: bool = False


@dataclass
class Display:
    """DISPLAY {一意名-1|定数-1}… [UPON 呼び名-1]. G 文法書 付録F §F.10.

    24976 statements over 2358 files. `upon` is separate because it names a
    DEVICE, not a value: 20530 statements have it and 19856 of those write
    `DISP`. One flat operand list reports the device as displayed output on 82%
    of them.
    """

    operands: list = field(default_factory=list)
    #: 呼び名-1 — DISP, CONSOLE, SYSOUT … Empty when the clause is absent.
    upon: str = ""


@dataclass
class Accept:
    """ACCEPT 一意名-1 [FROM {呼び名-1|DATE|DAY|DAY-OF-WEEK|TIME}].

    6135 statements over 2198 files, and 6037 of them write FROM — the bare form
    is the exception here, not the rule. `from_operand` keeps the word as
    written; DATE and TIME are compiler-supplied and DISP is a device, and this
    package does not need to tell them apart to record which was asked for.
    """

    target: str = ""
    from_operand: str = ""


@dataclass
class Stop:
    """STOP {RUN|定数-1}. G 文法書 付録F §F.10.

    3868 statements over 2560 files. 3450 write RUN; the other 418 stop with an
    operator message, and the two are different enough that a consumer must be
    able to tell them apart — one ends the run unconditionally, the other halts
    for an operator and can be resumed.
    """

    run: bool = False
    #: The message, quotes included, when the statement is not `STOP RUN`.
    literal: str = ""


@dataclass
class Exit:
    """EXIT / EXIT PROGRAM. G 文法書 付録F §F.10.

    31182 statements over 2330 files — the most common verb in this corpus.
    30916 are bare and 266 write PROGRAM, and they do different things: the bare
    form is a no-op that falls through to the next paragraph, `EXIT PROGRAM`
    returns to the caller. One field, because that is the whole difference.
    """

    program: bool = False


@dataclass
class Rewrite:
    """REWRITE. G 文法書 付録F §F.10 (sequential and relative/indexed forms).

    2319 statements over 821 files. The record name may be QUALIFIED — 45
    statements write `REWRITE B-REC OF BFILE` — and that is ONE operand: reading
    it as two would report the FILE as the record being rewritten.
    """

    record_name: str = ""
    from_operand: str | None = None


@dataclass
class Delete:
    """DELETE ファイル名-1 RECORD. G 文法書 付録F §F.10.

    265 statements over 178 files, and `RECORD` is a 補助語 — 78 statements write
    it and 187 do not, so the file name has to come from the same place either
    way.
    """

    file_name: str = ""


@dataclass
class Arithmetic:
    """ADD · SUBTRACT · MULTIPLY · DIVIDE — one record, one skeleton.

    G 文法書 §3.6.7 (ADD) · §3.6.44 (SUBTRACT) · §3.6.27 (MULTIPLY) ·
    §3.6.15 (DIVIDE), and 付録F §F.10 for all four.

    42027 statements with COMPUTE, which has its own record because it carries an
    expression rather than operands.

    **`giving` decides the data flow, and getting it backwards is silent.**
    Without GIVING the operand after the joining word IS the target: `ADD 1 TO N`
    changes N. With GIVING those operands are read only and the GIVING list is
    written: `ADD A B GIVING C` leaves A and B alone. `targets` answers that in
    one place so no consumer has to re-derive it.

    `keyword` is the joining word as written, and it may be ABSENT: all 224
    corpus `ADD … GIVING` statements over 48 files omit `TO`, while both
    §3.6.7.2 書き方2 and 付録F §F.10 print it as required. The documented form
    occurs zero times here; the undocumented one occurs always. SUBTRACT,
    MULTIPLY and DIVIDE always write theirs.

    `rounded` lists the target names that carry ROUNDED, not a flag: the manual
    attaches it to ONE target inside the repeated brace, so `GIVING A B ROUNDED`
    rounds B alone.

    `corresponding` and `remainder`: CORRESPONDING/CORR is 0 in this corpus and
    modelled because §F.10 gives it to ADD and SUBTRACT; REMAINDER is DIVIDE's
    alone and is real here — 624 statements over 301 files.
    """

    verb: str = ""
    sources: list = field(default_factory=list)
    #: "TO" | "FROM" | "BY" | "INTO" | "" — as written, absent on ADD … GIVING.
    keyword: str = ""
    #: Operands after the joining word and before GIVING.
    operands: list = field(default_factory=list)
    giving: list = field(default_factory=list)
    rounded: list = field(default_factory=list)
    corresponding: bool = False
    remainder: str = ""

    @property
    def targets(self) -> list:
        """What the statement WRITES. `giving` when present, else `operands`."""
        return self.giving or self.operands


@dataclass
class Compute:
    """COMPUTE. G 文法書 §3.6.11 · 付録F §F.10.

    17415 statements over 1594 files. Separate from `Arithmetic` because the
    right-hand side is an EXPRESSION, not a list of operands, and pretending
    otherwise would put arithmetic operators into an operand list.

    `expression` keeps the tokens as written. Evaluating or normalizing it is a
    different job with different failure modes; this package stops at the parse.
    """

    targets: list = field(default_factory=list)
    rounded: list = field(default_factory=list)
    expression: str = ""


@dataclass
class OpenFile:
    """One file inside an OPEN, with the mode that governs it."""

    mode: str = ""     # INPUT | OUTPUT | I-O | EXTEND
    name: str = ""
    no_rewind: bool = False


@dataclass
class Open:
    """A typed OPEN. G 文法書 付録F §F.10 (three forms) · E 文法書 付録4.

    7657 statements over 2650 files, and the design question is the list: one
    statement may open several files under several modes — `OPEN INPUT AFILE
    BFILE OUTPUT PRTFILE` is one statement with three files — and 2265 of them
    (30%) name two or more, up to nine and beyond. A record with a single
    `file_name` would keep the first and drop the rest, so the mode travels with
    each file rather than being a field of the statement.
    """

    files: list = field(default_factory=list)


@dataclass
class CloseFile:
    """One file inside a CLOSE."""

    name: str = ""
    #: "" | "NO REWIND" | "LOCK" — §F.10 gives NO REWIND to the sequential form
    #: and LOCK to all four. Both are 0 in this corpus, and that zero has a
    #: control: the grep that was meant to confirm it fired 87 times, all of them
    #: `WITH REVERSED ORDER` on START.
    option: str = ""


@dataclass
class Close:
    """A typed CLOSE. G 文法書 付録F §F.10 · E 文法書 付録4.

    6319 statements over 2648 files, and 2774 of them (44%) name two or more
    files. The single-name shape is the minority here, which is why this is a
    list for the same reason OPEN is.
    """

    files: list = field(default_factory=list)


@dataclass
class Read:
    """A typed READ — the union of the 書き方 across both dialects.

    G 文法書 §4.4.4.2 (sequential) · §5.4.5.2 (relative) · §6.4.5.2 (indexed)
    · §10.4.4.2 (display file) · E 文法書 付録4 (two forms, no terminator)

    13771 statements over 2629 files — the corpus's third most common verb — and
    until this record existed none of them had a file name.

    `direction` holds the read direction as written: NEXT · PRIOR · FIRST · LAST.
    All four are 書き方1 of **PRECOBOL**, the RDB precompiler dialect — ASP JIS
    COBOL E 使用手引書 第Ⅳ部 §5.4.5: 「順呼出し法の READ 命令は，ファイルの
    レコード参照範囲の**次，直前，最初又は最後**のレコードを使用可能にする」.
    That citation was found late: §6.4.5.2 of the G 文法書 (read from the page
    image), 付録F §F.10 and E's 付録4 all print `[NEXT]` alone, and an earlier
    version of this docstring concluded from that no manual documented PRIOR.
    It is documented — in the USAGE guide, not the grammar. Corpus: PRIOR 24
    statements over 19 files, and 19 of those files carry the `.PRC` extension,
    i.e. PRECOBOL source, which is exactly what the citation covers. FIRST and
    LAST are 0-hit here and modelled because the manual defines them.

    `key_operand` is the `KEY IS` clause, NOT `INVALID KEY`. The word `KEY`
    appears in 7325 statements; the clause is in 1158. START had the same trap at
    a factor of 1.6; here it is 6.3.
    """

    file_name: str = ""
    #: "NEXT" | "PRIOR" | "FIRST" | "LAST" | None — one slot, as written.
    direction: str | None = None
    into_operand: str | None = None
    key_operand: str | None = None
    #: 富士通拡張, 網掛け in both 書き方 of §6.4.5.2. Zero in this corpus for
    #: READ (it is 257 for START); modelled so a file that has it does not lose
    #: it silently.
    record_format: str | None = None


@dataclass
class Start:
    """A typed START. G 文法書 §6.4.7 · E 文法書 §5.4.6 書き方1.

    `key_relation` is normalized and `key_words` keeps what was written, because
    the two answer different questions. The corpus writes one relation two ways —
    `IS NOT <` 2039 times and `IS >=` 160 — and they mean the same thing, so a
    field holding only raw words makes `>=` look seven times rarer than it is.
    Normalizing alone would have thrown away the evidence for that claim, so both
    are kept.

    The equivalence `NOT <` ≡ `>=` is COBOL semantics, not something either
    manual states: §6.4.7 lists them as separate alternatives in the same brace.

    3582 statements; 2952 carry a KEY clause. An earlier version of this class
    reported 1873, and that number came from this parser while it was broken:
    `INVALID KEY` also spells KEY, the marker stays in the statement's own
    tokens, and reading the clause word by word let the SECOND match overwrite
    the first with the empty tail behind it. 1079 statements over 488 files are
    that shape. The whole-corpus check passed because it counted the relations
    it could read and called them all of them — 2952 - 1079 = 1873, consistent
    with itself and wrong. Clause heads are matched by POSITION here for that
    reason, never by the presence of the word.
    """

    file_name: str = ""
    #: "=" | ">" | ">=" | "<" | "<=" | "NOT =" | None
    key_relation: str | None = None
    #: The relation exactly as written, e.g. `IS NOT <`.
    key_words: str | None = None
    key_operand: str | None = None
    record_format: str | None = None
    #: `WITH REVERSED ORDER` — 83 statements over 49 files. 書き方2/3/4 of ASP
    #: COBOL G 使用手引書 §5.5.9 (the USAGE guide; the 文法書 prints only the
    #: ascending form, which is why an earlier note here said it was undocumented).
    #: It sets DESCENDING positioning, and the plain READs that follow then walk
    #: backwards — §5.5.9 works the example: `START … KEY IS <= … WITH REVERSED`
    #: points at record 8, and the next two READs give 8 then 7.
    reversed_order: bool = False
    #: `FIRST RECORD` — 書き方3: position at the SMALLEST key, or with
    #: `reversed_order` the LARGEST (the same example: record 1 vs record 15).
    #: 0-hit in this corpus; modelled because the manual defines it.
    first_record: bool = False
    #: `POSITIONING POINTER IS データ名-3` — 書き方4, 144 statements over 58
    #: files, and the value was landing nowhere until this field existed. It
    #: identifies ONE record among DUPLICATE keys, so dropping it loses which
    #: duplicate the program meant. (Same clause name as the SELECT clause that
    #: declares the pointer item; this is the START that uses it.)
    positioning_pointer: str | None = None


def _is_noise(tok) -> bool:
    return tok.type == "SEP" and tok.text in _NOISE


def _sig(tokens):
    """Significant tokens: no spacing, no comments."""
    return [t for t in tokens if t.type not in ("SPACE", "COMMENT", "COMMENT_ENTRY")]


def _text(tokens) -> str:
    """Reconstruct a clause's source text — literals keep their quotes, since
    `WS-EOF = 'Y'` and `WS-EOF = Y` are different conditions."""
    out = []
    for t in tokens:
        if _is_noise(t):
            continue
        out.append(f"{t.quote}{t.text}{t.quote}" if t.type == "STRING" else t.text)
    return " ".join(out)


def _operands(tokens) -> list[str]:
    """Operand HEADS, skipping qualification (`OF`/`IN` …) and subscripts (`( … )`)."""
    out: list[str] = []
    depth = 0
    skip_next = False
    for tok in tokens:
        text = tok.text
        # Judge by TYPE, never by text: `MOVE '(' TO H51` is a literal bracket,
        # and reading it as a subscript swallowed the rest of the statement.
        if tok.type == "SEP" and text == "(":
            depth += 1
            continue
        if tok.type == "SEP" and text == ")":
            depth = max(0, depth - 1)
            continue
        if depth or _is_noise(tok):
            continue
        if skip_next:
            skip_next = False
            continue
        upper = text.upper()
        # `OF`/`IN` introduce a qualifier — but only when something follows them.
        # `MOVE IN TO IFL-OPEN-MODE` uses IN as a data name, and treating it as a
        # qualifier left 20 corpus MOVEs with no source at all.
        if upper in ("OF", "IN") and tok is not tokens[-1]:
            skip_next = True
            continue
        if tok.type in ("WORD", "NUMBER"):
            out.append(text.upper())
        elif tok.type == "STRING":
            out.append(f"{tok.quote}{tok.text}{tok.quote}")
    return out


def _split_at(words: list[str], keyword: str) -> tuple[list, list]:
    """Tokens before / after the first standalone `keyword` (empty tail if absent)."""
    for i, tok in enumerate(words):
        if tok.type == "WORD" and tok.text.upper() == keyword:
            return words[:i], words[i + 1 :]
    return words, []


@dataclass
class Move:
    sources: list = field(default_factory=list)
    targets: list = field(default_factory=list)
    corresponding: bool = False
    source_is_literal: bool = False


@dataclass
class GoTo:
    targets: list = field(default_factory=list)
    depending_on: str = ""


@dataclass
class Perform:
    target: str = ""
    thru: str = ""
    times: str = ""
    until: str = ""
    varying: str = ""
    from_: str = ""
    by: str = ""
    test: str = ""  # "" | BEFORE | AFTER


@dataclass
class Call:
    target: str = ""
    target_is_literal: bool = False
    using: list = field(default_factory=list)
    by_mode: dict = field(default_factory=dict)


@dataclass
class Select:
    """A FILE-CONTROL entry (付録F §F.3), including the Fujitsu extensions.

    §F.3.3 (pdf p417) puts `POSITIONING POINTER IS` and `RECORD FORMAT IS` on the
    SELECT, shaded — they are extensions, and this corpus uses them on 81 and 117
    files. Reading them off the entry is what lets a migration ask which files
    depend on ASP-only index behaviour, since NetCOBOL has no direct equivalent.

    A caution about what two of these fields HOLD. `record_format` and
    `positioning_pointer` are DATA NAMES, not the thing they name. 文法書 §6.2.7:
    `RECORD FORMAT IS データ名-1` requires データ名-1 to be an 8-character
    alphanumeric item declared in WORKING-STORAGE or LINKAGE, and it is that item's
    RUNTIME VALUE that names the record format — the clause is only legal when the
    RDM file merges several physical files. So `record_format == "GREC-FORMAT"`
    means "the format is whatever GREC-FORMAT holds at run time", never "the layout
    is called GREC-FORMAT". Resolving it statically to a record definition would be
    wrong, and wrong in the quiet way: the name looks like a layout name.
    """
    name: str = ""
    optional: bool = False
    assign: str = ""
    organization: str = ""       # SEQUENTIAL | RELATIVE | INDEXED
    access_mode: str = ""        # SEQUENTIAL | RANDOM | DYNAMIC
    record_key: list = field(default_factory=list)
    relative_key: str = ""       # 0 in this corpus
    file_status: str = ""
    duplicates: bool = False           # RECORD KEY … WITH DUPLICATES  (拡張)
    positioning_pointer: str = ""      # 富士通拡張
    record_format: str = ""            # 富士通拡張
    destination_2: str = ""
    #: `DESTINATION AREA IS データ名-1` — 付録B.1, 67 clauses over 60 files.
    #: B.1.1: 「機能は，DESTINATION-1 句と同様である」 — the SAME function as
    #: `DESTINATION-1`, so a consumer after that value should read
    #: `destination_1 or destination_area`. Kept as its own field because the two
    #: spellings are evidence of which form the program used, and because it is a
    #: legacy interchange spec: 付録B's preamble says these 「共通プログラム開発
    #: には使用すべきではない」. Syntactically it is 8 alphanumeric characters,
    #: never in the FILE SECTION (B.1.3).
    #: It also SHARES a head with SYMBOLIC DESTINATION: adding `DESTINATION` as a
    #: head made all 67 read their own `AREA` as the destination until this
    #: field existed.
    destination_area: str = ""            # DESTINATION-2 IS     0 in this corpus

    #: 表示ファイル — 文法書 Chương 10 §10.2.3.2. Absent from 付録F entirely, which
    #: is why these were dropped on up to 939 files before being modelled.
    format_name: str = ""              # FORMAT IS            939 files
    group_name: str = ""               # GROUP IS             830
    destination_1: str = ""            # DESTINATION-1 IS     745
    unit_control: str = ""             # UNIT CONTROL IS      717
    symbolic_destination: str = ""     # SYMBOLIC DESTINATION 454 (a literal)
    processing_mode: str = ""          # PROCESSING MODE IS   454
    selected_function: str = ""        # SELECTED FUNCTION IS 397
    #: 表10.1 lists 15 clauses for a display-file SELECT. These six had no field
    #: and their values were dropped without a trace. All 0-hit in this corpus
    #: (ACM/APL destinations only) — which ranks them low, and is not a reason to
    #: keep losing them: NOMINAL KEY was 0-hit too, right up until it was measured
    #: at 139 files.
    processing_time: str = ""          # PROCESSING TIME IS      0
    message_class: str = ""            # MESSAGE CLASS IS        0
    message_code: str = ""             # MESSAGE CODE IS         0
    message_mode: str = ""             # MESSAGE MODE IS         0
    message_owner: str = ""            # MESSAGE OWNER IS        0
    session_control: str = ""          # SESSION CONTROL IS      0

    #: ASP JIS COBOL E 付録4 only — `NOMINAL` occurs zero times in either COBOL G
    #: manual, yet the corpus writes it. The corpus is mixed-dialect.
    nominal_key: str = ""              # 139 files
    actual_key: str = ""               # 9 files


def _parse_move(tokens) -> Move:
    body = _sig(tokens)[1:]  # drop the verb
    out = Move()
    if body and body[0].type == "WORD" and body[0].text.upper() in ("CORRESPONDING", "CORR"):
        out.corresponding = True
        body = body[1:]
    src, dst = _split_at(body, "TO")
    out.sources = _operands(src)
    out.targets = _operands(dst)
    out.source_is_literal = bool(src) and src[0].type in ("STRING", "NUMBER")
    return out


def _parse_go_to(tokens) -> GoTo:
    body = _sig(tokens)[1:]
    if body and body[0].type == "WORD" and body[0].text.upper() == "TO":
        body = body[1:]
    head, dep = _split_at(body, "DEPENDING")
    out = GoTo(targets=_operands(head))
    if dep:
        if dep and dep[0].type == "WORD" and dep[0].text.upper() == "ON":
            dep = dep[1:]
        names = _operands(dep)
        out.depending_on = names[0] if names else ""
    return out


_PERFORM_CLAUSES = ("VARYING", "UNTIL", "TIMES", "THRU", "THROUGH", "WITH")


def _parse_perform(tokens) -> Perform:
    body = _sig(tokens)[1:]
    out = Perform()

    # The procedure name comes first, before any clause keyword. A count only
    # ends the name when TIMES is actually present — a paragraph may legitimately
    # be named with digits (`PERFORM 100-INIT`, or even `PERFORM 100`).
    has_times = any(t.type == "WORD" and t.text.upper() == "TIMES" for t in body)
    head: list = []
    i = 0
    while i < len(body):
        tok = body[i]
        if tok.type == "WORD" and tok.text.upper() in _PERFORM_CLAUSES:
            break
        if has_times and tok.type == "NUMBER":
            break
        head.append(tok)
        i += 1
    names = _operands(head)
    if names:
        out.target = names[0]
    rest = body[i:]

    # THRU / THROUGH 手続き名-2
    for kw in ("THRU", "THROUGH"):
        before, after = _split_at(rest, kw)
        if after:
            thru = _operands(after[:1])
            out.thru = thru[0] if thru else ""
            rest = before + after[1:]
            break

    # WITH TEST BEFORE|AFTER
    before, after = _split_at(rest, "TEST")
    if after and after[0].type == "WORD" and after[0].text.upper() in ("BEFORE", "AFTER"):
        out.test = after[0].text.upper()
        rest = before + after[1:]
    rest = [t for t in rest if not (t.type == "WORD" and t.text.upper() == "WITH")]

    # VARYING 一意名-2 FROM … BY … — read before UNTIL, which closes the clause
    before, after = _split_at(rest, "VARYING")
    if after:
        var_part, until_part = _split_at(after, "UNTIL")
        names = _operands(var_part[:1])
        out.varying = names[0] if names else ""
        _, frm = _split_at(var_part, "FROM")
        if frm:
            frm_head, _ = _split_at(frm, "BY")
            vals = _operands(frm_head)
            out.from_ = vals[0] if vals else ""
        _, by = _split_at(var_part, "BY")
        if by:
            vals = _operands(by)
            out.by = vals[0] if vals else ""
        if until_part:
            out.until = _text(until_part)
        return out

    # 一意名-1|整数-1 TIMES — the count sits immediately BEFORE the keyword
    if has_times:
        before, after = _split_at(rest, "TIMES")
        vals = _operands(before)
        if vals:
            out.times = vals[-1]
        rest = after

    # UNTIL 条件-1
    _, until = _split_at(rest, "UNTIL")
    if until:
        out.until = _text(until)
    return out


def _parse_call(tokens) -> Call:
    body = _sig(tokens)[1:]
    out = Call()
    if not body:
        return out
    head = body[0]
    if head.type == "STRING":
        out.target, out.target_is_literal = head.text.upper(), True
    elif head.type == "WORD":
        out.target = head.text.upper()

    _, using = _split_at(body, "USING")
    if not using:
        return out
    mode = "REFERENCE"  # 7.5.2: BY REFERENCE is the default
    i = 0
    skip_qualifier = False
    while i < len(using):
        tok = using[i]
        upper = tok.text.upper() if tok.type == "WORD" else ""
        # `USING NODAY1 OF FJ1481FM` — the qualifier is part of the SAME argument,
        # so neither `OF` nor the record after it is an argument of its own.
        if skip_qualifier:
            skip_qualifier = False
            i += 1
            continue
        if upper in ("OF", "IN") and i + 1 < len(using):
            skip_qualifier = True
            i += 1
            continue
        if upper == "BY" and i + 1 < len(using):
            nxt = using[i + 1].text.upper()
            if nxt in ("REFERENCE", "CONTENT", "VALUE"):
                mode = nxt
                i += 2
                continue
        if upper in ("ON", "OVERFLOW", "EXCEPTION", "END-CALL", "GIVING", "RETURNING"):
            break
        for name in _operands([tok]):
            out.using.append(name)
            out.by_mode[name] = mode
        i += 1
    return out


#: Words that end the clause being collected inside a SELECT. Kept as a set of
#: FIRST words: every clause below is introduced by one of them.
#: EVERY clause head the manuals name, whether or not this corpus uses it. A head
#: that is missing does not merely go untyped — it GLUES onto the clause before it,
#: so the neighbour is silently corrupted too. Listing the whole set costs nothing:
#: a head with no branch below falls through unhandled, which loses nothing and
#: invents nothing. Sources: 付録F §F.3 (順/相対/索引), 文法書 Chương 10 §10.2.3.2
#: (表示ファイル — absent from 付録F), JIS COBOL E 付録4 (NOMINAL/ACTUAL KEY).
_SELECT_CLAUSE_HEADS = frozenset((
    # §F.3
    "ASSIGN", "ORGANIZATION", "ACCESS", "RECORD", "RELATIVE", "FILE",
    "POSITIONING", "RESERVE", "ALTERNATE", "PASSWORD", "LOCK", "SHARING",
    # Chương 10 — 表示ファイル
    "FORMAT", "GROUP", "SYMBOLIC", "DESTINATION-1", "DESTINATION-2",
    # §10.2.3.2, read from the page image: SYMBOLIC / MODE / SELECTED /
    # FILE carry no underline, so each of these four clauses may begin at
    # its SECOND word. Without them as heads the clause glues onto its
    # neighbour and its value is lost — 1081 clauses over ~400 files.
    "DESTINATION", "STATUS", "FUNCTION",
    "PROCESSING", "SELECTED", "UNIT", "MESSAGE", "SESSION",
    # JIS COBOL E 付録4
    "NOMINAL", "ACTUAL", "FILE-LIMIT", "FILE-LIMITS",
))
#: `WITH` is deliberately NOT a clause head: the only WITH in §F.3 is
#: `RECORD KEY … WITH DUPLICATES`, and cutting there would strand the flag in a
#: clause of its own where the key parser can never see it.
#: Filler inside a SELECT clause: present or absent without changing the meaning.
_SELECT_NOISE = frozenset(("IS", "ARE", "TO", "MODE", "KEY", "STATUS", "POINTER"))


#: Two-word clause names whose SECOND word is also a head. Cutting between them
#: splits one clause into two, and the tail half then overwrites a different field:
#: `ALTERNATE RECORD KEY IS A-ALT` replaced the primary `record_key`, and
#: `RECORD FORMAT IS X` landed in `format_name` (the 表示 clause) instead of
#: `record_format`. Both were caused by adding a head that was correct on its own.
_SELECT_GLUED_PAIRS = frozenset((
    ("ALTERNATE", "RECORD"),   # ALTERNATE RECORD KEY
    ("RECORD", "FORMAT"),      # RECORD FORMAT IS  (富士通拡張, vs 表示 FORMAT IS)
))


def _select_clauses(body) -> list[list]:
    """Cut a SELECT entry into its clauses, each starting at a clause head."""
    out: list[list] = []
    cur: list = []
    prev = ""
    for tok in body:
        word = tok.text.upper() if tok.type == "WORD" else ""
        cuts = (word in _SELECT_CLAUSE_HEADS and cur
                and (prev, word) not in _SELECT_GLUED_PAIRS)
        if cuts:
            out.append(cur)
            cur = [tok]
        else:
            cur.append(tok)
        if word:
            prev = word
    if cur:
        out.append(cur)
    return out


def _select_values(clause, drop: int) -> list[str]:
    """Operands of a clause, with its keywords and filler removed."""
    rest = [t for t in clause[drop:]
            if not (t.type == "WORD" and t.text.upper() in _SELECT_NOISE)]
    return _operands(rest)


def _parse_select(tokens) -> Select:
    body = _sig(tokens)[1:]  # drop SELECT
    out = Select()
    if body and body[0].type == "WORD" and body[0].text.upper() == "OPTIONAL":
        out.optional = True
        body = body[1:]

    # The file name runs until the first clause head.
    head: list = []
    while body and not (body[0].type == "WORD"
                        and body[0].text.upper() in _SELECT_CLAUSE_HEADS):
        head.append(body[0])
        body = body[1:]
    names = _operands(head)
    if names:
        out.name = names[0]

    for clause in _select_clauses(body):
        words = [t.text.upper() for t in clause if t.type == "WORD"]
        if not words:
            continue
        first, second = words[0], (words[1] if len(words) > 1 else "")

        if first == "ASSIGN":
            vals = _select_values(clause, 1)
            out.assign = vals[0] if vals else ""
        elif first == "ORGANIZATION":
            vals = [w for w in words[1:] if w != "IS"]
            out.organization = vals[0] if vals else ""
        elif first == "ACCESS":
            vals = [w for w in words[1:] if w not in ("MODE", "IS")]
            out.access_mode = vals[0] if vals else ""
        elif first == "RECORD" and second == "KEY":
            # `WITH DUPLICATES` is a flag, not another key — dropping it into the
            # list would invent a data name that does not exist.
            keys = [t for t in clause[2:]]
            if "DUPLICATES" in words:
                out.duplicates = True
                keys = [t for t in keys
                        if not (t.type == "WORD"
                                and t.text.upper() in ("WITH", "DUPLICATES"))]
            out.record_key = _select_values(keys, 0)
        elif first == "RECORD" and second == "FORMAT":
            vals = _select_values(clause, 2)
            out.record_format = vals[0] if vals else ""
        elif first == "RELATIVE":
            vals = _select_values(clause, 1)
            out.relative_key = vals[0] if vals else ""
        elif first == "FILE" and second == "STATUS":
            vals = _select_values(clause, 2)
            out.file_status = vals[0] if vals else ""
        elif first == "STATUS":
            # FILE is the 補助語, omitted on 11 clauses / 11 files.
            vals = _select_values(clause, 1)
            out.file_status = vals[0] if vals else ""
        elif first == "POSITIONING":
            vals = _select_values(clause, 1)
            out.positioning_pointer = vals[0] if vals else ""

        # 表示ファイル — Chương 10 §10.2.3.2
        elif first == "FORMAT":
            vals = _select_values(clause, 1)
            out.format_name = vals[0] if vals else ""
        elif first == "GROUP":
            vals = _select_values(clause, 1)
            out.group_name = vals[0] if vals else ""
        elif first == "SYMBOLIC" and second == "DESTINATION":
            # 定数-1, a LITERAL not a data name. `_operands` already renders a
            # literal with its quotes, and keeping that shape matters: '"DSP"' and
            # DSP are a constant and an identifier, not two spellings of one thing.
            vals = _select_values(clause, 2)
            out.symbolic_destination = vals[0] if vals else ""
        elif first == "DESTINATION" and second == "AREA":
            # 付録B.1.2, not the SYMBOLIC DESTINATION clause. Tested BEFORE the
            # short form below, or that branch reads `AREA` as the destination.
            vals = _select_values(clause, 2)
            out.destination_area = vals[0] if vals else ""
        elif first == "DESTINATION":
            # SYMBOLIC is the 補助語 — no underline in §10.2.3.2 — and 499 clauses
            # over 352 files omit it. `DESTINATION-1` / `-2` are single tokens, so
            # they cannot reach here.
            vals = _select_values(clause, 1)
            out.symbolic_destination = vals[0] if vals else ""
        elif first == "DESTINATION-1":
            vals = _select_values(clause, 1)
            out.destination_1 = vals[0] if vals else ""
        elif first == "DESTINATION-2":
            vals = _select_values(clause, 1)
            out.destination_2 = vals[0] if vals else ""
        elif first == "PROCESSING" and second == "TIME":
            vals = _select_values(clause, 2)
            out.processing_time = vals[0] if vals else ""
        elif first == "MESSAGE" and second in ("CLASS", "CODE", "MODE", "OWNER"):
            vals = _select_values(clause, 2)
            setattr(out, "message_" + second.lower(), vals[0] if vals else "")
        elif first == "SESSION" and second == "CONTROL":
            vals = _select_values(clause, 2)
            out.session_control = vals[0] if vals else ""
        elif first == "PROCESSING" and second == "MODE":
            vals = _select_values(clause, 2)
            out.processing_mode = vals[0] if vals else ""
        elif first == "PROCESSING":
            # MODE is a 補助語 (no underline in §10.2.3.2) and 498 clauses over
            # 351 files omit it. Reached only after the TIME and MODE branches
            # above, so `PROCESSING TIME` keeps its own field.
            vals = _select_values(clause, 1)
            out.processing_mode = vals[0] if vals else ""
        elif first == "SELECTED" and second == "FUNCTION":
            vals = _select_values(clause, 2)
            out.selected_function = vals[0] if vals else ""
        elif first == "FUNCTION":
            # SELECTED is the 補助語 here, omitted on 73 clauses / 68 files.
            vals = _select_values(clause, 1)
            out.selected_function = vals[0] if vals else ""
        elif first == "UNIT" and second == "CONTROL":
            vals = _select_values(clause, 2)
            out.unit_control = vals[0] if vals else ""

        # JIS COBOL E 付録4
        elif first == "NOMINAL" and second == "KEY":
            vals = _select_values(clause, 2)
            out.nominal_key = vals[0] if vals else ""
        elif first == "ACTUAL" and second == "KEY":
            vals = _select_values(clause, 2)
            out.actual_key = vals[0] if vals else ""
    return out


@dataclass
class FileDescription:
    """An FD/SD entry — 付録F §F.6 (five organisations, pdf 420-421).

    Only four of its clauses occur in this corpus, and the counts are why the rest
    have no field: LABEL RECORD on 2994 files, BLOCK CONTAINS 2200, LINAGE 165,
    DATA RECORD 81. RECORD CONTAINS, VALUE OF, RECORDING MODE, CODE-SET,
    IS EXTERNAL/GLOBAL, RECORD IS VARYING and LINES AT TOP/BOTTOM are all zero —
    RECORD CONTAINS was measured twice by different routes because zero looked
    wrong for a COBOL corpus. It is absent.
    """
    name: str = ""
    is_sort: bool = False              # SD rather than FD
    block_contains: str = ""
    block_unit: str = ""               # RECORDS | CHARACTERS
    label_records: str = ""            # STANDARD | OMITTED
    data_records: list = field(default_factory=list)
    linage: str = ""
    footing: str = ""


@dataclass
class DataDescription:
    """A data description entry — 付録F §F.7 (pdf 422, a figure page).

    511495 of them here. Ordered by files: PIC 5455, VALUE 3099, REDEFINES 2994,
    OCCURS 2103, COMP-3 1794, PACKED-DECIMAL 964, and `CHARACTER TYPE` — shaded in
    the manual, so a Fujitsu extension — on 161.
    """
    level: str = ""
    name: str = ""
    redefines: str = ""
    picture: str = ""
    usage: str = ""                    # COMP | COMP-3 | BINARY | PACKED-DECIMAL …
    occurs: str = ""
    occurs_to: str = ""                # OCCURS n TO m … DEPENDING ON
    depending_on: str = ""
    indexed_by: list = field(default_factory=list)
    keys: list = field(default_factory=list)     # (ASCENDING|DESCENDING, name)
    value: str = ""
    sync: bool = False
    justified: bool = False
    blank_when_zero: bool = False
    character_type: str = ""           # 富士通拡張
    renames: str = ""


#: USAGE can be written bare, without the keyword — 1165 COMPs and 20897 COMP-3s
#: in this corpus are written that way, against 28 uses of `USAGE`.
_USAGES = frozenset((
    "COMPUTATIONAL", "COMP", "COMPUTATIONAL-3", "COMP-3", "COMPUTATIONAL-4",
    "COMP-4", "BINARY", "PACKED-DECIMAL", "DISPLAY", "INDEX", "BIT", "POINTER",
))


def _first_operand(tokens) -> str:
    """The first real operand, skipping separators.

    `_operands(rest[:1])` was wrong whenever a separator sat between a keyword and
    its operand — `06 / WS-R REDEFINES / WS-A` put a `/` in that slot, `_operands`
    dropped it as punctuation, and the field came back empty on 33 files that
    plainly stated a REDEFINES target. Scan forward instead of trusting position.
    """
    for tok in tokens:
        if tok.type in ("WORD", "NUMBER", "STRING"):
            vals = _operands([tok])
            if vals:
                return vals[0]
    return ""


def _after(words, tokens, *keyword) -> list:
    """Tokens following a keyword sequence, or []."""
    n = len(keyword)
    for i in range(len(words) - n + 1):
        if words[i:i + n] == list(keyword):
            return tokens[i + n:]
    return []


def _parse_file_description(tokens) -> FileDescription:
    sig = _sig(tokens)
    words = [t.text.upper() if t.type == "WORD" else "" for t in sig]
    out = FileDescription(is_sort=bool(words) and words[0] == "SD")
    if len(sig) > 1:
        out.name = sig[1].text.upper()

    rest = _after(words, sig, "BLOCK", "CONTAINS")
    if rest:
        out.block_contains = _first_operand(rest[:3])
        for t in rest[:4]:
            if t.type == "WORD" and t.text.upper() in ("RECORDS", "CHARACTERS"):
                out.block_unit = t.text.upper()
                break

    for kw in (("LABEL", "RECORD"), ("LABEL", "RECORDS")):
        rest = _after(words, sig, *kw)
        if rest:
            for t in rest[:3]:
                if t.type == "WORD" and t.text.upper() in ("STANDARD", "OMITTED"):
                    out.label_records = t.text.upper()
                    break
            break

    for kw in (("DATA", "RECORD"), ("DATA", "RECORDS")):
        rest = _after(words, sig, *kw)
        if rest:
            head = [t for t in rest
                    if not (t.type == "WORD" and t.text.upper() in ("IS", "ARE"))]
            stop = ("LINAGE", "BLOCK", "LABEL", "VALUE", "RECORD", "RECORDING", "CODE-SET")
            names = []
            for t in head:
                if t.type == "WORD" and t.text.upper() in stop:
                    break
                names.append(t)
            out.data_records = _operands(names)
            break

    rest = _after(words, sig, "LINAGE")
    if rest:
        out.linage = _first_operand(
            [t for t in rest[:3] if not (t.type == "WORD" and t.text.upper() == "IS")])
    # `WITH` is optional and this corpus omits it: `LINAGE 66 FOOTING 66` on 10
    # files. Keying on FOOTING alone catches both spellings.
    rest = _after(words, sig, "FOOTING")
    if rest:
        out.footing = _first_operand(
            [t for t in rest[:3] if not (t.type == "WORD" and t.text.upper() == "AT")])
    return out


def _parse_data_description(tokens) -> DataDescription:
    sig = _sig(tokens)
    words = [t.text.upper() if t.type == "WORD" else "" for t in sig]
    out = DataDescription()
    if sig:
        out.level = sig[0].text.zfill(2) if sig[0].type == "NUMBER" else sig[0].text.upper()
    if len(sig) > 1 and sig[1].type == "WORD":
        out.name = sig[1].text.upper()

    for kw in (("PICTURE",), ("PIC",)):
        rest = _after(words, sig, *kw)
        if rest:
            body = [t for t in rest if not (t.type == "WORD" and t.text.upper() == "IS")]
            # The picture string is ONE token here: the lexer keeps `X(10)` and
            # `S9(7)V99` whole, so taking more would swallow the next clause.
            out.picture = body[0].text if body else ""
            break

    rest = _after(words, sig, "USAGE")
    if rest:
        for t in rest[:3]:
            if t.type == "WORD" and t.text.upper() in _USAGES:
                out.usage = t.text.upper()
                break
    if not out.usage:
        for t in sig[2:]:
            if t.type == "WORD" and t.text.upper() in _USAGES:
                out.usage = t.text.upper()
                break

    rest = _after(words, sig, "REDEFINES")
    if rest:
        out.redefines = _first_operand(rest[:3])

    rest = _after(words, sig, "RENAMES")
    if rest:
        out.renames = _first_operand(rest[:3])

    rest = _after(words, sig, "OCCURS")
    if rest:
        out.occurs = _first_operand(rest[:3])
        to = _after(words, sig, "TO")
        if to and out.occurs:
            out.occurs_to = _first_operand(to[:3])
        dep = _after(words, sig, "DEPENDING", "ON")
        if dep:
            out.depending_on = _first_operand(dep[:3])
    idx = _after(words, sig, "INDEXED", "BY")
    if idx:
        stop = ("PIC", "PICTURE", "VALUE", "OCCURS", "REDEFINES")
        names = []
        for t in idx:
            if t.type == "WORD" and t.text.upper() in stop:
                break
            names.append(t)
        out.indexed_by = _operands(names)
    for order in ("ASCENDING", "DESCENDING"):
        rest = _after(words, sig, order)
        if rest:
            body = [t for t in rest[:4]
                    if not (t.type == "WORD" and t.text.upper() in ("KEY", "IS"))]
            vals = _operands(body[:1])
            if vals:
                out.keys.append((order, vals[0]))

    rest = _after(words, sig, "VALUE")
    if not rest:
        rest = _after(words, sig, "VALUES")
    if rest:
        body = [t for t in rest if not (t.type == "WORD" and t.text.upper() in ("IS", "ARE"))]
        if body:
            out.value = (f"{body[0].quote}{body[0].text}{body[0].quote}"
                         if body[0].type == "STRING" else body[0].text)

    ct = _after(words, sig, "CHARACTER", "TYPE")
    if ct:
        body = [t for t in ct if not (t.type == "WORD" and t.text.upper() == "IS")]
        out.character_type = body[0].text.upper() if body else ""

    upper = set(words)
    out.sync = bool(upper & {"SYNCHRONIZED", "SYNC"})
    out.justified = bool(upper & {"JUSTIFIED", "JUST"})
    out.blank_when_zero = ["BLANK", "WHEN", "ZERO"] == words[-3:] or bool(
        _after(words, sig, "BLANK", "WHEN", "ZERO")
    )
    return out


def parse_entry(entry):
    """Typed clauses for a DATA DIVISION entry — FD/SD or a level number."""
    if entry.level in ("FD", "SD"):
        return _parse_file_description(entry.tokens)
    return _parse_data_description(entry.tokens)


#: Words that end the operand of whatever clause is being read.
_WRITE_STOPS = frozenset((
    "FROM", "BEFORE", "AFTER", "ADVANCING", "POSITIONING", "AT", "NOT",
    "INVALID", "END-WRITE", "RECORD", "LINE", "LINES",
))


def _parse_write(tokens) -> Write:
    """WRITE, read clause by clause rather than by position.

    `ADVANCING` is a 補助語: §4.4.7.2 prints it without an underline, and the
    corpus omits it in 3314 of 4178 statements that write BEFORE/AFTER. So the
    operand is taken from after BEFORE/AFTER and the word, if present, is simply
    stepped over — requiring it would lose the majority.
    """
    body = _sig(tokens)[1:]  # drop the verb
    out = Write()
    words = [t.text.upper() if t.type == "WORD" else t.text for t in body]

    if body:
        out.record_name = _first_operand(body)

    for i, w in enumerate(words):
        rest = body[i + 1:]
        if w == "FROM":
            out.from_operand = _first_operand(rest)
        elif w in ("BEFORE", "AFTER"):
            nxt = rest[0].text.upper() if rest and rest[0].type == "WORD" else ""
            if nxt == "POSITIONING":
                # E §5.4.8 書き方2 — `AFTER POSITIONING` is its own clause, and the
                # AFTER belongs to it, not to an omitted ADVANCING.
                out.positioning = _first_operand(rest[1:])
                continue
            out.advancing = w
            if nxt == "ADVANCING":
                rest = rest[1:]
            out.advancing_operand = _first_operand(rest)
        elif w == "POSITIONING" and out.positioning is None:
            out.positioning = _first_operand(rest)
        elif w == "RECORD" and len(words) > i + 1 and words[i + 1] == "FORMAT":
            #  is a 補助語 here and in every other clause of this shape; the
            # operand is whatever follows it, or follows FORMAT when it is left out.
            tail = rest[1:]
            if tail and tail[0].type == "WORD" and tail[0].text.upper() in ("IS", "ARE"):
                tail = tail[1:]
            out.record_format = _first_operand(tail)
    return out


#: Spelling → relation. `IS` is a 補助語 and is stripped before the lookup: 203
#: of 2978 corpus KEY clauses leave it out.
_RELATIONS = {
    "=": "=", "EQUAL TO": "=", "EQUAL": "=",
    ">": ">", "GREATER THAN": ">", "GREATER": ">",
    "<": "<", "LESS THAN": "<", "LESS": "<",
    ">=": ">=", "GREATER THAN OR EQUAL TO": ">=",
    "NOT <": ">=", "NOT LESS THAN": ">=", "NOT LESS": ">=",
    "<=": "<=", "LESS THAN OR EQUAL TO": "<=",
    "NOT >": "<=", "NOT GREATER THAN": "<=", "NOT GREATER": "<=",
    "NOT =": "NOT =", "NOT EQUAL TO": "NOT =",
}


#: Joining word per verb. DIVIDE writes both (`BY` 215, `INTO` 552).
_ARITH_KEYWORDS = {
    "ADD": ("TO",), "SUBTRACT": ("FROM",), "MULTIPLY": ("BY",),
    "DIVIDE": ("BY", "INTO"),
}
#: Words that end an operand run inside an arithmetic statement.
_ARITH_STOPS = frozenset((
    "TO", "FROM", "BY", "INTO", "GIVING", "ROUNDED", "REMAINDER",
    "ON", "SIZE", "ERROR", "NOT", "END-ADD", "END-SUBTRACT", "END-MULTIPLY",
    "END-DIVIDE", "CORRESPONDING", "CORR",
))


def _arith_run(body, start: int, rounded: list) -> tuple[list, int]:
    """Operands from `start` until a clause word, recording ROUNDED per name.

    ROUNDED binds to the name BEFORE it — the manual puts it inside the repeated
    brace, `{一意名-3 [ROUNDED]} …`, so `GIVING A B ROUNDED` rounds B and not A.
    A statement-level flag would round both.
    """
    names: list = []
    chunk: list = []
    i = start

    def flush():
        # `_operands` must see the whole run: it is what folds `A OF B` and
        # `A (I)` into one name. Called per token it returned three operands for
        # `WS-T OF WS-REC` and made every subscript index a separate target —
        # which is how 109 corpus statements came to look like they had 2 or 3
        # targets with one ROUNDED between them. They have one target each.
        if chunk:
            names.extend(_operands(chunk))
            chunk.clear()

    while i < len(body):
        tok = body[i]
        up = tok.text.upper() if tok.type == "WORD" else ""
        if up in _ARITH_STOPS:
            if up == "ROUNDED":
                flush()
                if names:
                    rounded.append(names[-1])
                i += 1
                continue
            break
        chunk.append(tok)
        i += 1
    flush()
    return names, i


#: Words inside a condition that are syntax, not operands. Figurative constants
#: are values a program cannot write to, so they are not "what the condition
#: reads" either.
_COND_NOISE = frozenset((
    "AND", "OR", "NOT", "IS", "ARE", "THEN", "EQUAL", "EQUALS", "GREATER",
    "LESS", "THAN", "TO", "NEXT", "SENTENCE", "OF", "IN",
    "ZERO", "ZEROS", "ZEROES", "SPACE", "SPACES", "HIGH-VALUE", "HIGH-VALUES",
    "LOW-VALUE", "LOW-VALUES", "QUOTE", "QUOTES", "ALL",
    "NUMERIC", "ALPHABETIC", "POSITIVE", "NEGATIVE",
))


def _without_grouping(cond: list) -> list:
    """Drop GROUPING parentheses, keep SUBSCRIPT ones.

    `_operands` folds `NAME (index)` into the name, which is what a subscript
    should do and the opposite of what a grouped condition needs: `(WS-J > 20)
    AND (WS-K < 41)` has no name in front of its `(`, so the whole group was
    swallowed and the statement read as having no operands. 3002 corpus
    conditions open with a paren — the field looked populated on 97% of IFs and
    was empty exactly where the conditions were hardest.

    A `(` opens a SUBSCRIPT when the token before it is a USER name — a WORD the
    lexer did not mark reserved. Testing "is a WORD" alone is not enough: in
    `… AND (WS-K < 41)` the paren follows `AND`, so the group read as a subscript
    of AND and swallowed WS-K. A reserved word is never a subscripted item,
    because a program cannot name one. The matching `)` is decided by the same
    stack, so a subscript inside a group survives.
    """
    out, stack, prev = [], [], None
    for tok in cond:
        text = tok.text
        if tok.type == "SEP" and text == "(":
            subscript = (prev is not None and prev.type == "WORD"
                         and not prev.reserved)
            stack.append(subscript)
            if subscript:
                out.append(tok)
        elif tok.type == "SEP" and text == ")":
            if stack.pop() if stack else False:
                out.append(tok)
        elif tok.type != "NUMBER":
            out.append(tok)
        prev = tok
    return out


def _parse_if(tokens) -> If:
    """IF 条件 [THEN] … — the condition is everything up to THEN / NEXT SENTENCE.

    The tree hands this the IF's OWN tokens, which stop before the arms, so the
    end of the condition is either the optional `THEN`, a trailing `NEXT
    SENTENCE`, or the end.
    """
    body = _sig(tokens)[1:]
    out = If()
    end = len(body)
    for i, tok in enumerate(body):
        up = tok.text.upper() if tok.type == "WORD" else ""
        if up == "THEN":
            out.has_then = True
            end = min(end, i)
        elif (up == "NEXT" and i + 1 < len(body)
                and body[i + 1].type == "WORD"
                and body[i + 1].text.upper() == "SENTENCE"):
            out.then_next_sentence = True
            end = min(end, i)
    cond = body[:end]
    out.condition = " ".join(
        f"{t.quote}{t.text}{t.quote}" if t.type == "STRING" else t.text for t in cond
    ).strip()
    out.condition_operands = [
        x for x in _operands(_without_grouping(cond))
        if x.upper() not in _COND_NOISE and not x.startswith(("'", '"'))
    ]
    return out


def _parse_display(tokens) -> Display:
    """DISPLAY, split at UPON so the device never joins the operand list."""
    body = _sig(tokens)[1:]
    out = Display()
    cut = next((i for i, t in enumerate(body)
                if t.type == "WORD" and t.text.upper() == "UPON"), -1)
    left = body if cut < 0 else body[:cut]
    out.operands = _operands(left)
    if cut >= 0:
        out.upon = _first_operand(body[cut + 1:])
    return out


def _parse_accept(tokens) -> Accept:
    """ACCEPT 一意名-1 [FROM …]."""
    body = _sig(tokens)[1:]
    out = Accept()
    cut = next((i for i, t in enumerate(body)
                if t.type == "WORD" and t.text.upper() == "FROM"), -1)
    left = body if cut < 0 else body[:cut]
    out.target = _first_operand(left)
    if cut >= 0:
        out.from_operand = _first_operand(body[cut + 1:])
    return out


def _parse_stop(tokens) -> Stop:
    """STOP {RUN|定数-1} — the literal keeps its quotes, like a MOVE source."""
    body = _sig(tokens)[1:]
    out = Stop()
    if body and body[0].type == "WORD" and body[0].text.upper() == "RUN":
        out.run = True
    elif body:
        tok = body[0]
        out.literal = (f"{tok.quote}{tok.text}{tok.quote}"
                       if tok.type == "STRING" else tok.text)
    return out


def _parse_exit(tokens) -> Exit:
    """EXIT / EXIT PROGRAM — one field, because that is the whole difference."""
    body = _sig(tokens)[1:]
    return Exit(program=bool(body) and body[0].type == "WORD"
                and body[0].text.upper() == "PROGRAM")


def _parse_rewrite(tokens) -> Rewrite:
    """REWRITE レコード名-1 [FROM 一意名-1]."""
    body = _sig(tokens)[1:]
    out = Rewrite()
    if body:
        out.record_name = _first_operand(body)
    for i, tok in enumerate(body):
        if tok.type == "WORD" and tok.text.upper() == "FROM":
            out.from_operand = _first_operand(body[i + 1:])
            break
    return out


def _parse_delete(tokens) -> Delete:
    """DELETE ファイル名-1 RECORD — `RECORD` is filler, never the operand."""
    body = _sig(tokens)[1:]
    out = Delete()
    if body:
        out.file_name = _first_operand(body)
    return out


def _parse_arithmetic(tokens) -> Arithmetic:
    """ADD / SUBTRACT / MULTIPLY / DIVIDE, read as one shape."""
    sig = _sig(tokens)
    verb = sig[0].text.upper() if sig else ""
    body = sig[1:]
    out = Arithmetic(verb=verb)
    joins = _ARITH_KEYWORDS.get(verb, ())

    i = 0
    if body and body[0].type == "WORD" and body[0].text.upper() in ("CORRESPONDING", "CORR"):
        out.corresponding = True
        i = 1

    out.sources, i = _arith_run(body, i, out.rounded)
    if i < len(body):
        up = body[i].text.upper() if body[i].type == "WORD" else ""
        if up in joins:
            out.keyword = up
            out.operands, i = _arith_run(body, i + 1, out.rounded)

    while i < len(body):
        up = body[i].text.upper() if body[i].type == "WORD" else ""
        if up == "GIVING":
            out.giving, i = _arith_run(body, i + 1, out.rounded)
            continue
        if up == "REMAINDER":
            rest, i = _arith_run(body, i + 1, out.rounded)
            out.remainder = rest[0] if rest else ""
            continue
        break
    return out


def _parse_compute(tokens) -> Compute:
    """COMPUTE {一意名 [ROUNDED]} … = 算術式.

    Split at the `=` rather than scanned for clause words: everything right of it
    is the expression and may contain any operator, including `=` inside a
    relation the compiler allows.
    """
    body = _sig(tokens)[1:]
    out = Compute()
    cut = next((i for i, t in enumerate(body) if t.type == "OP" and t.text == "="), -1)
    left = body if cut < 0 else body[:cut]
    out.targets, _ = _arith_run(left, 0, out.rounded)
    if cut >= 0:
        out.expression = " ".join(t.text for t in body[cut + 1:]).strip()
    return out


#: The four OPEN modes of §F.10. `I-O` is one word to the lexer (the hyphen is
#: part of a COBOL word), so it needs no special case.
_OPEN_MODES = ("INPUT", "OUTPUT", "I-O", "EXTEND")


def _parse_open(tokens) -> Open:
    """OPEN, one entry per file, each carrying the mode in force.

    The mode is a MODE and the words after it are FILES until the next mode, so
    the loop keeps state instead of matching each word independently. `WITH NO
    REWIND` attaches to the file it follows, not to the statement.
    """
    body = _sig(tokens)[1:]
    out = Open()
    mode = ""
    i = 0
    while i < len(body):
        tok = body[i]
        w = tok.text.upper() if tok.type == "WORD" else ""
        if w in _OPEN_MODES:
            mode = w
        elif w == "WITH" or w == "REWIND":
            pass
        elif w == "NO":
            if out.files:
                out.files[-1].no_rewind = True
        elif tok.type == "WORD":
            out.files.append(OpenFile(mode=mode, name=tok.text))
        i += 1
    return out


def _parse_close(tokens) -> Close:
    """CLOSE, one entry per file. `WITH LOCK` / `WITH NO REWIND` attach to the
    file they follow, so the option is on the entry and not on the statement."""
    body = _sig(tokens)[1:]
    out = Close()
    i = 0
    while i < len(body):
        tok = body[i]
        w = tok.text.upper() if tok.type == "WORD" else ""
        if w == "WITH":
            pass
        elif w == "LOCK":
            if out.files:
                out.files[-1].option = "LOCK"
        elif w == "NO":
            if out.files:
                out.files[-1].option = "NO REWIND"
        elif w == "REWIND":
            pass
        elif tok.type == "WORD":
            out.files.append(CloseFile(name=tok.text))
        i += 1
    return out


def _parse_read(tokens) -> Read:
    """READ, read clause by clause.

    Two words carry double duty and both are resolved by POSITION, never by
    presence:

      `RECORD`  is the 補助語 right after the file name AND the head of
                `RECORD FORMAT IS`. Matching the first occurrence takes the
                noise word on every `READ f NEXT RECORD`.
      `KEY`     heads the `KEY IS` clause AND the `INVALID KEY` arm. Matching
                the word gives 7325 statements a key clause; 1158 have one.

    The AT END / INVALID KEY arms are not fields here — the scope machinery owns
    them, and duplicating them would give two answers to one question.
    """
    body = _sig(tokens)[1:]  # drop the verb
    out = Read()
    words = [t.text.upper() if t.type == "WORD" else t.text for t in body]
    if body:
        out.file_name = _first_operand(body)

    for i, w in enumerate(words):
        rest = body[i + 1:]
        if i == 1 and w in ("NEXT", "PRIOR", "FIRST", "LAST"):
            out.direction = w
        elif w == "INTO":
            out.into_operand = _first_operand(rest)
        elif w == "KEY" and (i == 0 or words[i - 1] != "INVALID"):
            tail = rest
            if tail and tail[0].type == "WORD" and tail[0].text.upper() in ("IS", "ARE"):
                tail = tail[1:]
            out.key_operand = _first_operand(tail)
        elif w == "RECORD" and len(words) > i + 1 and words[i + 1] == "FORMAT":
            tail = rest[1:]
            if tail and tail[0].type == "WORD" and tail[0].text.upper() in ("IS", "ARE"):
                tail = tail[1:]
            out.record_format = _first_operand(tail)
    return out


def _parse_start(tokens) -> Start:
    """START, read clause by clause.

    The KEY relation is collected as the run of relational words after KEY and
    looked up whole rather than matched piecewise: `NOT <` and `<` are opposite
    relations, and taking the first symbol seen would turn 2039 statements that
    mean `>=` into `<`.
    """
    body = _sig(tokens)[1:]  # drop the verb
    out = Start()
    words = [t.text.upper() if t.type in ("WORD", "OP") else t.text for t in body]
    if body:
        out.file_name = _first_operand(body)

    for i, w in enumerate(words):
        rest = body[i + 1:]
        if w == "REVERSED":
            out.reversed_order = True
        elif w == "FIRST" and len(words) > i + 1 and words[i + 1] == "RECORD":
            out.first_record = True
        elif w == "POSITIONING" and len(words) > i + 1 and words[i + 1] == "POINTER":
            tail = body[i + 2:]
            if tail and tail[0].type == "WORD" and tail[0].text.upper() in ("IS", "ARE"):
                tail = tail[1:]
            out.positioning_pointer = _first_operand(tail)
        elif w == "KEY" and (i == 0 or words[i - 1] != "INVALID"):
            run, j = [], i + 1
            while j < len(words) and words[j] in (
                "IS", "NOT", "EQUAL", "GREATER", "LESS", "THAN", "OR", "TO",
                "=", ">", "<", ">=", "<=",
            ):
                run.append(words[j])
                j += 1
            out.key_words = " ".join(run) or None
            key = " ".join(x for x in run if x != "IS")
            out.key_relation = _RELATIONS.get(key)
            out.key_operand = _first_operand(body[j:])
        elif w == "RECORD" and len(words) > i + 1 and words[i + 1] == "FORMAT":
            tail = rest[1:]
            if tail and tail[0].type == "WORD" and tail[0].text.upper() in ("IS", "ARE"):
                tail = tail[1:]
            out.record_format = _first_operand(tail)
    return out


@dataclass
class StringGroup:
    """One `{一意名-1}… DELIMITED [BY] {一意名-2|定数-2|SIZE}` group."""
    sources: list = field(default_factory=list)
    delimiter: str = ""


@dataclass
class String:
    groups: list = field(default_factory=list)
    into: str = ""
    pointer: str = ""

    @property
    def sources(self) -> list:
        """Every source operand in order — what the statement READS."""
        return [s for g in self.groups for s in g.sources]


def _parse_string(tokens) -> String:
    """STRING {一意名-1|定数-1}… DELIMITED [BY] {一意名-2|定数-2|SIZE} …
    INTO 一意名-3 [WITH POINTER 一意名-4].

    `BY` is a 補助語: §3.6.25.2 underlines DELIMITED, SIZE, INTO and POINTER
    and leaves BY, WITH and ON plain. The corpus agrees — 215 DELIMITED
    clauses, only 145 `BY` — so requiring it would read SIZE as the delimited
    operand on 70 clauses. This one was checked on the page image BEFORE the
    parser was written; the same question cost 1081 SELECT clauses when it was
    answered from the text layer, where underlines do not survive.

    Each group carries its own delimiter. Flattening the sources into one list
    would say WS-C below is delimited by SPACE:

        STRING WS-A WS-B DELIMITED BY SPACE  WS-C DELIMITED BY '#' INTO …
    """
    body = _sig(tokens)[1:]
    out = String()
    head, tail = _split_at(body, "INTO")
    if tail:
        out.into = _first_operand(tail)
        words = [t.text.upper() if t.type == "WORD" else "" for t in tail]
        if "POINTER" in words:
            out.pointer = _first_operand(tail[words.index("POINTER") + 1:])
    pending, i = [], 0
    while i < len(head):
        tok = head[i]
        if tok.type == "WORD" and tok.text.upper() == "DELIMITED":
            j = i + 1
            if j < len(head) and head[j].type == "WORD" and head[j].text.upper() == "BY":
                j += 1
            while j < len(head) and head[j].type not in ("WORD", "NUMBER", "STRING"):
                j += 1
            out.groups.append(StringGroup(
                sources=_operands(pending),
                delimiter=_operands(head[j:j + 1])[0] if j < len(head) else "",
            ))
            pending, i = [], j + 1
            continue
        pending.append(tok)
        i += 1
    return out


@dataclass
class InspectTally:
    counter: str = ""
    scope: str = ""      # ALL | LEADING | CHARACTERS
    operand: str = ""    # empty for CHARACTERS, which counts every one


@dataclass
class InspectReplace:
    scope: str = ""      # ALL | LEADING | FIRST | CHARACTERS
    from_operand: str = ""
    to_operand: str = ""


@dataclass
class Inspect:
    target: str = ""
    tallying: list = field(default_factory=list)
    replacing: list = field(default_factory=list)


_INSPECT_SCOPES = ("ALL", "LEADING", "FIRST", "CHARACTERS")


def _parse_inspect(tokens) -> Inspect:
    """INSPECT 一意名-1 [TALLYING {一意名-2 FOR {CHARACTERS|{ALL|LEADING} x}…}…]
    [REPLACING {{ALL|LEADING|FIRST} x BY y | CHARACTERS BY y}…].

    A statement may carry both phrases, so they are separate lists rather than
    a mode field. 66 corpus statements TALLY and 19 REPLACE; none of the 85
    writes BEFORE/AFTER INITIAL, which is why no field holds it — the ledger
    records that as a form the corpus does not exercise rather than as covered.
    """
    body = _sig(tokens)[1:]
    out = Inspect()
    head, rest = _split_at(body, "TALLYING")
    tally, replace = rest, []
    if not rest:
        head, replace = _split_at(body, "REPLACING")
    else:
        tally, replace = _split_at(rest, "REPLACING")
    out.target = _first_operand(head)

    words = [t.text.upper() if t.type == "WORD" else "" for t in tally]
    counter = ""
    for i, tok in enumerate(tally):
        w = words[i]
        if w == "FOR":
            counter = _first_operand(tally[:i][::-1]) or counter
        elif w == "CHARACTERS":
            out.tallying.append(InspectTally(counter=counter, scope="CHARACTERS"))
        elif w in ("ALL", "LEADING"):
            out.tallying.append(InspectTally(
                counter=counter, scope=w,
                operand=_first_operand(tally[i + 1:])))

    words = [t.text.upper() if t.type == "WORD" else "" for t in replace]
    for i, tok in enumerate(replace):
        w = words[i]
        if w not in _INSPECT_SCOPES:
            continue
        arm = replace[i + 1:]
        arm_words = words[i + 1:]
        by = arm_words.index("BY") if "BY" in arm_words else -1
        if w == "CHARACTERS":
            out.replacing.append(InspectReplace(
                scope=w, to_operand=_first_operand(arm[by + 1:]) if by >= 0 else ""))
        else:
            out.replacing.append(InspectReplace(
                scope=w,
                from_operand=_first_operand(arm[:by] if by >= 0 else arm),
                to_operand=_first_operand(arm[by + 1:]) if by >= 0 else ""))
    return out


@dataclass
class Examine:
    target: str = ""
    mode: str = ""          # TALLYING | REPLACING
    scope: str = ""         # ALL | LEADING | FIRST | UNTIL FIRST
    from_operand: str = ""
    to_operand: str = ""    # the BY value


def _parse_examine(tokens) -> Examine:
    """EXAMINE 一意名 {TALLYING {ALL|LEADING|UNTIL FIRST} 定数-1 [REPLACING BY 定数-2]
    | REPLACING {ALL|LEADING|FIRST} 定数-3 BY 定数-4}.

    JIS COBOL E only — 付録4 旧仕様. COBOL G dropped it for INSPECT, so every
    one of these has to become an INSPECT during migration, which needs the
    scope and both literals apart. All 44 corpus statements are the REPLACING
    form: ALL 38, LEADING 6.
    """
    body = _sig(tokens)[1:]
    out = Examine()
    out.target = _first_operand(body)
    words = [t.text.upper() if t.type == "WORD" else "" for t in body]
    for i, w in enumerate(words):
        if w in ("TALLYING", "REPLACING") and not out.mode:
            out.mode = w
        elif w == "UNTIL" and i + 1 < len(words) and words[i + 1] == "FIRST":
            out.scope = "UNTIL FIRST"
            out.from_operand = _first_operand(body[i + 2:])
        elif w in _INSPECT_SCOPES and not out.scope:
            out.scope = w
            out.from_operand = _first_operand(body[i + 1:])
        elif w == "BY":
            out.to_operand = _first_operand(body[i + 1:])
    return out


@dataclass
class Release:
    record_name: str = ""
    from_operand: str | None = None


def _parse_release(tokens) -> Release:
    """RELEASE レコード名-1 [FROM 一意名-1] — the SORT-side twin of REWRITE."""
    body = _sig(tokens)[1:]
    out = Release()
    if body:
        out.record_name = _first_operand(body)
    for i, tok in enumerate(body):
        if tok.type == "WORD" and tok.text.upper() == "FROM":
            out.from_operand = _first_operand(body[i + 1:])
            break
    return out


@dataclass
class SameArea:
    """One `SAME [RECORD] AREA FOR …` clause."""
    record_area: bool = False
    files: list = field(default_factory=list)


@dataclass
class Same:
    """Every SAME clause of one I-O-CONTROL sentence."""
    areas: list = field(default_factory=list)


def _parse_same(sentence_tokens) -> Same:
    """SAME [RECORD] AREA FOR ファイル名-1 {ファイル名-2}… (§4.2.10.2).

    I-O-CONTROL is a single sentence holding every clause in the paragraph, so
    one sentence can carry several SAME clauses — 57 corpus sentences carry
    one and one carries three. Returning a record per sentence would drop two
    of those three, which is how the first measurement of this clause came out
    as "58 clauses, one of them naming six files": it was counting sentences.

    `RECORD` is bracketed, and the forms are not interchangeable — SAME AREA
    (20 clauses) shares the whole buffer and forbids the files being open
    together, SAME RECORD AREA (40) shares only the record area and allows it.
    """
    body = _sig(sentence_tokens)
    out = Same()
    starts = [i for i, t in enumerate(body)
              if t.type == "WORD" and t.text.upper() == "SAME"]
    for k, i in enumerate(starts):
        end = starts[k + 1] if k + 1 < len(starts) else len(body)
        clause = body[i + 1:end]
        words = [t.text.upper() if t.type == "WORD" else "" for t in clause]
        area = SameArea(record_area=bool(words) and words[0] == "RECORD")
        if "FOR" in words:
            area.files = _operands(clause[words.index("FOR") + 1:])
        out.areas.append(area)
    return out


@dataclass
class Copy:
    name: str = ""
    library: str = ""
    replacing: list = field(default_factory=list)   # (from, to) word pairs
    joining: str = ""
    joining_as: str = ""                            # PREFIX | SUFFIX


def _parse_copy_stmt(tokens) -> Copy:
    """COPY 原文名-1 [OF|IN 登録集名-1] [REPLACING …] [JOINING 語-3 [TO ALL NAMES]
    AS {PREFIX|SUFFIX}] — 付録B.2 / §9.2.2.

    The clauses are cut by `expand._parse_copy`, which already had to read them
    to decide what text to pull in. Reusing it is the point: a second parse of
    the same statement can disagree with the first, and then the statement view
    and the expanded view name different copybooks with nothing to flag it.

    Known limit, stated rather than discovered later: a REPLACING operand is
    taken as WORD tokens, so pseudo-text delimiters (`==:TAG:==`) come back as
    the words inside them. 11 corpus statements use REPLACING at all.
    """
    from .expand import _parse_copy  # local: expand sits below this layer

    d = _parse_copy(tokens)
    return Copy(name=d["name"], library=d["lib"],
                replacing=[(a.text.upper(), b.text.upper()) for a, b in d["replacing"]],
                joining=d["joining"], joining_as=d["as"])


@dataclass
class Initialize:
    targets: list = field(default_factory=list)
    replacing: list = field(default_factory=list)   # (category, value)


def _parse_initialize(tokens) -> Initialize:
    """INITIALIZE {一意名-1}… [REPLACING {分類} DATA BY {一意名-2|定数-1}]…

    §3.6.17.2 was a figure; both the body transcription and 付録F.10 print the
    same form, which is two independent readings of one page. 12319 of the
    13289 corpus statements name exactly one item and none writes REPLACING.
    """
    body = _sig(tokens)[1:]
    out = Initialize()
    head, tail = _split_at(body, "REPLACING")
    out.targets = _operands(head)
    words = [t.text.upper() if t.type == "WORD" else "" for t in tail]
    for i, w in enumerate(words):
        if w == "DATA" and i + 1 < len(words) and words[i + 1] == "BY":
            category = next((x for x in reversed(words[:i]) if x), "")
            out.replacing.append((category, _first_operand(tail[i + 2:])))
    return out


@dataclass
class Continue:
    """CONTINUE takes no operand — §3.6.10.2 is one word.

    An empty record is not the same as no record: it says the statement was
    read and there is nothing in it, which `parsed is None` cannot say. 4797
    statements over 1070 files sat in the work queue for exactly this.
    """


def _parse_continue(tokens) -> Continue:
    return Continue()


@dataclass
class Evaluate:
    subjects: list = field(default_factory=list)
    subject_is_condition: bool = False   # EVALUATE TRUE / FALSE


def _parse_evaluate(tokens) -> Evaluate:
    """EVALUATE {一意名|定数|式|TRUE|FALSE} [ALSO …]… — the WHEN arms are not
    here: `tree()` keeps them as the statement's `branches`, which is what makes
    `EVALUATE TRUE … WHEN <condition>` readable as a decision table."""
    body = _sig(tokens)[1:]
    out = Evaluate()
    group: list = []
    for tok in body:
        if tok.type == "WORD" and tok.text.upper() == "ALSO":
            out.subjects.extend(_operands(group))
            group = []
            continue
        group.append(tok)
    out.subjects.extend(_operands(group))
    out.subject_is_condition = any(s in ("TRUE", "FALSE") for s in out.subjects)
    return out


@dataclass
class Return:
    file_name: str = ""
    into: str = ""


def _parse_return(tokens) -> Return:
    """RETURN ファイル名-1 [RECORD] [INTO 一意名-1] AT END … — §8.4.3.2.

    The 書き方 prints RECORD without brackets, and all 17 corpus statements
    leave it out. Treating it as required would give every one of them no file
    name at all; it is read as a 補助語, the same as on READ and DELETE.
    """
    body = _sig(tokens)[1:]
    out = Return()
    out.file_name = _first_operand(body)
    words = [t.text.upper() if t.type == "WORD" else "" for t in body]
    if "INTO" in words:
        out.into = _first_operand(body[words.index("INTO") + 1:])
    return out


@dataclass
class Set:
    targets: list = field(default_factory=list)
    mode: str = ""      # TO | UP BY | DOWN BY
    value: str = ""


def _parse_set(tokens) -> Set:
    """SET … TO … | SET … UP BY … | SET … DOWN BY … | SET … TO TRUE — §3.6.23.2
    書き方 1-4. The four forms differ only in the keyword between the targets
    and the value, so one record with a `mode` says which without four types."""
    body = _sig(tokens)[1:]
    out = Set()
    words = [t.text.upper() if t.type == "WORD" else "" for t in body]
    for i, w in enumerate(words):
        if w in ("UP", "DOWN"):
            out.mode = f"{w} BY"
            out.targets = _operands(body[:i])
            rest = body[i + 1:]
            if words[i + 1:i + 2] == ["BY"]:
                rest = body[i + 2:]
            out.value = _first_operand(rest)
            return out
        if w == "TO":
            out.mode = "TO"
            out.targets = _operands(body[:i])
            out.value = _first_operand(body[i + 1:])
            return out
    out.targets = _operands(body)
    return out


@dataclass
class Sort:
    file_name: str = ""
    keys: list = field(default_factory=list)      # (ASCENDING|DESCENDING, [names])
    input_procedure: str = ""
    output_procedure: str = ""
    using: list = field(default_factory=list)
    giving: list = field(default_factory=list)
    duplicates: bool = False


_SORT_HEADS = ("ASCENDING", "DESCENDING", "INPUT", "OUTPUT", "USING", "GIVING",
               "WITH", "COLLATING", "ON")


def _parse_sort(tokens) -> Sort:
    """SORT ファイル名-1 [ON] {ASCENDING|DESCENDING} KEY {データ名}… …
    {INPUT PROCEDURE IS 手続き名 | USING {ファイル名}…}
    {OUTPUT PROCEDURE IS 手続き名 | GIVING ファイル名} — §8.4.4.2.

    `ON` before the key direction is optional: 1 of the 17 corpus statements
    writes it. Procedures and USING/GIVING are alternatives, and 16 of 17 use
    procedures — a record carrying only USING/GIVING would be empty on nearly
    all of them.
    """
    body = _sig(tokens)[1:]
    out = Sort()
    out.file_name = _first_operand(body)
    words = [t.text.upper() if t.type == "WORD" else "" for t in body]

    def run(start: int) -> list:
        """Operands from `start` until the next clause head."""
        chunk = []
        for k in range(start, len(body)):
            if words[k] in _SORT_HEADS or words[k] in ("KEY", "PROCEDURE", "IS"):
                break
            chunk.append(body[k])
        return _operands(chunk)

    for i, w in enumerate(words):
        if w in ("ASCENDING", "DESCENDING"):
            j = i + 1
            if words[j:j + 1] == ["KEY"]:
                j += 1
            if words[j:j + 1] == ["IS"]:
                j += 1
            out.keys.append((w, run(j)))
        elif w in ("INPUT", "OUTPUT") and words[i + 1:i + 2] == ["PROCEDURE"]:
            j = i + 2
            if words[j:j + 1] == ["IS"]:
                j += 1
            name = _first_operand(body[j:])
            if w == "INPUT":
                out.input_procedure = name
            else:
                out.output_procedure = name
        elif w == "USING":
            out.using = run(i + 1)
        elif w == "GIVING":
            out.giving = run(i + 1)
        elif w == "DUPLICATES":
            out.duplicates = True
    return out


@dataclass
class Search:
    table: str = ""
    all_form: bool = False    # SEARCH ALL — a binary search, different semantics
    varying: str = ""


def _parse_search(tokens) -> Search:
    """SEARCH [ALL] 一意名-1 [VARYING {一意名-2|指標名-1}] [AT END …] — §3.6.22.2.

    `ALL` is not decoration: 書き方2 is a binary search over an ordered table
    and needs the table's keys declared, so a migration has to tell the two
    apart. All 17 corpus statements are the serial form.
    """
    body = _sig(tokens)[1:]
    out = Search()
    words = [t.text.upper() if t.type == "WORD" else "" for t in body]
    start = 0
    if words[:1] == ["ALL"]:
        out.all_form = True
        start = 1
    out.table = _first_operand(body[start:])
    if "VARYING" in words:
        out.varying = _first_operand(body[words.index("VARYING") + 1:])
    return out


@dataclass
class Lock:
    """LOCK UP … / UNLOCK … — the two are opposites, so the verb is a field.

    A consumer holding only `files` cannot tell "take the exclusive lock" from
    "release it", and the two statements are otherwise identical.
    """
    verb: str = ""                                # LOCK | UNLOCK
    files: list = field(default_factory=list)


def _parse_lock(tokens) -> Lock:
    """LOCK UP ファイル名-1 [ファイル名-2]… (E §13.4)
    UNLOCK ファイル名-1 [ファイル名-2]… (E §13.5)

    The verb of a LOCK is TWO words — read `UP` as an operand and it becomes
    the locked file on all 85 corpus statements. UNLOCK is the same clause
    without it, so the `UP` is skipped when present rather than required.
    Both take up to 10 files; every corpus statement names one, which is
    exactly when a singular field looks correct and is not.
    """
    toks = _sig(tokens)
    verb = toks[0].text.upper() if toks else ""
    body = toks[1:]
    if body and body[0].type == "WORD" and body[0].text.upper() == "UP":
        body = body[1:]
    return Lock(verb=verb, files=_operands(body))


@dataclass
class Trace:
    mode: str = ""                                # READY | RESET


def _parse_trace(tokens) -> Trace:
    """{READY|RESET} TRACE (E §8.3).

    TRACE is the object, not the verb: `READY TRACE` starts printing the name
    of every section and paragraph entered, `RESET TRACE` stops it. The mode is
    the entire difference, which is why it is the field.
    """
    toks = _sig(tokens)
    return Trace(mode=toks[0].text.upper() if toks else "")


@dataclass
class Entry:
    name: str = ""                                # 定数-1, a literal
    using: list = field(default_factory=list)


def _parse_entry(tokens) -> Entry:
    """ENTRY 定数-1 [USING データ名-1 [データ名-2]…] (E §9.3.4).

    The whole section is 網掛け: an alternate entry point into a called
    program is a Fujitsu extension, not JIS. Only the first 8 characters of
    the literal identify the entry point (構文規則 a), and 6 of the 8 corpus
    statements carry USING — those names are the called program's interface.
    """
    body = _sig(tokens)[1:]
    out = Entry(name=_first_operand(body))
    words = [t.text.upper() if t.type == "WORD" else "" for t in body]
    if "USING" in words:
        out.using = _operands(body[words.index("USING") + 1:])
    return out


@dataclass
class Exhibit:
    mode: str = ""                                # NAMED | CHANGED NAMED | CHANGED
    operands: list = field(default_factory=list)


def _parse_exhibit(tokens) -> Exhibit:
    """EXHIBIT {NAMED|CHANGED NAMED|CHANGED} {一意名-1|定数-1} […]… (E §8.4).

    The three modes print different things: `NAMED` prints name=value every
    time, `CHANGED NAMED` prints only the ones whose value moved since the last
    execution, `CHANGED` prints the moved values without their names. Testing
    for `CHANGED` before `CHANGED NAMED` would read the two-word mode as the
    one-word one and lose the names, so the longer form is matched first.
    """
    body = _sig(tokens)[1:]
    words = [t.text.upper() if t.type == "WORD" else "" for t in body]
    out = Exhibit()
    if words[:2] == ["CHANGED", "NAMED"]:
        out.mode, n = "CHANGED NAMED", 2
    elif words[:1] == ["CHANGED"]:
        out.mode, n = "CHANGED", 1
    elif words[:1] == ["NAMED"]:
        out.mode, n = "NAMED", 1
    else:
        n = 0
    out.operands = _operands(body[n:])
    return out


#: verb → clause parser. A verb absent here stays recognized but untyped.
REGISTRY = {
    "MOVE": _parse_move,
    "GO": _parse_go_to,
    "PERFORM": _parse_perform,
    "CALL": _parse_call,
    "WRITE": _parse_write,
    "START": _parse_start,
    "READ": _parse_read,
    "OPEN": _parse_open,
    "ADD": _parse_arithmetic,
    "SUBTRACT": _parse_arithmetic,
    "MULTIPLY": _parse_arithmetic,
    "DIVIDE": _parse_arithmetic,
    "COMPUTE": _parse_compute,
    "REWRITE": _parse_rewrite,
    "DELETE": _parse_delete,
    "DISPLAY": _parse_display,
    "ACCEPT": _parse_accept,
    "STOP": _parse_stop,
    "EXIT": _parse_exit,
    "IF": _parse_if,
    "CLOSE": _parse_close,
    "STRING": _parse_string,
    "INSPECT": _parse_inspect,
    "EXAMINE": _parse_examine,
    "RELEASE": _parse_release,
    "COPY": _parse_copy_stmt,
    "INITIALIZE": _parse_initialize,
    "CONTINUE": _parse_continue,
    "EVALUATE": _parse_evaluate,
    "RETURN": _parse_return,
    "SET": _parse_set,
    "SORT": _parse_sort,
    "SEARCH": _parse_search,
    "LOCK": _parse_lock,
    "UNLOCK": _parse_lock,
    "READY": _parse_trace,
    "RESET": _parse_trace,
    "ENTRY": _parse_entry,
    "EXHIBIT": _parse_exhibit,
}

#: head word → clause parser, for SENTENCES that are not statements. A SELECT is
#: a FILE-CONTROL entry, so it never reaches `REGISTRY`, which is keyed by verb.
CLAUSE_REGISTRY = {
    "SELECT": _parse_select,
    "SAME": _parse_same,
}

#: DATA DIVISION clause head -> the field it fills on `DataDescription` or
#: `FileDescription`. These clauses are typed by a FIELD rather than by an entry
#: in a registry, so nothing else here could see them: the coverage ledger asked
#: REGISTRY / CLAUSE_REGISTRY / _SELECT_CLAUSE_HEADS and filed all of them as
#: work still to do — VALUE on 3099 files, REDEFINES 2981, BLOCK CONTAINS 2843,
#: OCCURS 1560, straight to the top of the STEP-08 queue, months after they were
#: written. A wrong ledger does not look wrong; it looks like a plan.
#:
#: `test_registry.py` proves each pair by parsing a snippet and checking the
#: field fills, so a name here cannot drift away from what the parser does.
ENTRY_CLAUSES = {
    "REDEFINES": "redefines",
    "RENAMES": "renames",
    "OCCURS": "occurs",
    "PICTURE": "picture",
    "PIC": "picture",
    "USAGE": "usage",
    "VALUE": "value",
    "VALUES": "value",
    "INDEXED": "indexed_by",
    "CHARACTER": "character_type",
    "SYNCHRONIZED": "sync",
    "SYNC": "sync",
    "JUSTIFIED": "justified",
    "JUST": "justified",
    "BLANK": "blank_when_zero",
    "DEPENDING": "depending_on",
    "ASCENDING": "keys",
    "DESCENDING": "keys",
    # FileDescription
    "BLOCK": "block_contains",
    "LABEL": "label_records",
    "DATA": "data_records",
    "LINAGE": "linage",
    "FOOTING": "footing",
}

#: PROCEDURE-level clause head -> the mechanism that reads it.
#:
#: `ENTRY_CLAUSES` covers clauses typed by a field on a DATA DIVISION record.
#: These are read by something else again, and the coverage ledger could see
#: neither — so after that table landed it still reported three constructs the
#: parser has always handled as work to do: `FILLER` on 2548 files, `ROUNDED` on
#: 223, `SIZE` on 46. A work queue that names finished work is not a smaller
#: problem than one that hides work; this one had already sent me to the wrong
#: task twice.
#:
#: The three mechanisms are genuinely different, which is why the value here is
#: prose rather than a field name — and why `test_registry.py` proves each one by
#: exercising it rather than by reading this table.
STATEMENT_CLAUSES = {
    "ROUNDED": "a field: Arithmetic.rounded / Compute.rounded",
    "SIZE": "tree structure: the `ON SIZE ERROR` arm becomes the statement's body",
    "FILLER": "the NAME: DataEntry.name is literally FILLER",
}

#: Multi-word DATA DIVISION clauses that SHARE a head with something in
#: `ENTRY_CLAUSES` but are a different clause and are NOT read.
#:
#: `VALUE OF` is a FILE description clause (§4.3.8) and `VALUE` is a data-entry
#: clause; `FileDescription` has no field for the former. Head-word matching let
#: it inherit the latter's state and report itself as modelled — the same defect
#: as filing VALUE untyped, pointing the other way, and the more dangerous
#: direction: a queue that omits work looks finished.
#:
#: It stays uncovered rather than getting a field because the corpus uses it 0
#: times and the manual calls it 廃要素 — §5.3.2.4(6): 「VALUE OF 句は，廃要素で
#: あり，今後この要素は削除される予定である」. That is a decision, so it is
#: written down; if a file ever uses it, this line is where to start.
ENTRY_CLAUSES_UNCOVERED = frozenset(("VALUE OF",))


#: Words that HEAD a statement in the flat view but carry no clauses of their
#: own — they are read by the TREE (`Sentence.tree()`), so having no entry in
#: `REGISTRY` is the design, not a gap.
#:
#: Without this written down, the only available number was "132963 statements
#: with no registry parser", which reads as a hole a third the size of the
#: corpus. The real split over 867674 statements is:
#:
#:   734711  84.7%  typed by a registry parser
#:    52329   6.0%  scope terminators, END-*
#:    27666   3.2%  ELSE
#:    17476   2.0%  WHEN
#:     2067   0.2%  NOT
#:    33425   3.9%  a verb with no parser  <- the only real work in the number
#:
#: `test_registry.py` proves each mechanism by parsing a snippet: the markers
#: must be ABSENT from `tree()` and `WHEN` must be present under `branches`, so
#: a word cannot be parked here to make a queue look shorter.
TREE_TYPED_HEADS = {
    "ELSE": "marker: the statements after it become the owning IF's else_body",
    "WHEN": "kept as a node under the EVALUATE's `branches`",
    "NOT": "marker: opens the NOT ON SIZE ERROR / NOT INVALID KEY arm",
}


def is_tree_typed(verb: str) -> bool:
    """Does the TREE read this word, rather than a parser in `REGISTRY`?

    Every `END-*` is a scope terminator — the rule is the prefix, not a list,
    because the two dialects between them close 17 different verbs and a list
    would go stale the first time one more was written down.
    """
    return verb.startswith("END-") or verb in TREE_TYPED_HEADS


def parse_statement(statement):
    """Type a statement's clauses, or return None for a verb with no parser."""
    parser = REGISTRY.get(statement.verb)
    if parser is None:
        return None
    return parser(statement.tokens)


def parse_clause(sentence):
    """Type a clause sentence, or return None when its head has no parser."""
    toks = _sig(sentence.tokens)
    if not toks or toks[0].type != "WORD":
        return None
    parser = CLAUSE_REGISTRY.get(toks[0].text.upper())
    if parser is None:
        return None
    return parser(sentence.tokens)
