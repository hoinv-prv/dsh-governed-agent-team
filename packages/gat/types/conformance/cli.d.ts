import type{ConformanceDispatch}from'./index.d.ts';import type{ExecutionPacket,LoadedExecutionPacket,RuntimeEvidence}from'./runtime.d.ts';
export interface CliDependencies{environment?:Record<string,string|undefined>;loadPacket?:(options:{environment:Record<string,string|undefined>})=>Promise<LoadedExecutionPacket>;loadDispatcher?:(options:{executionPacket:ExecutionPacket})=>Promise<Readonly<{dispatch:ConformanceDispatch;runtimeEvidence:RuntimeEvidence}>>;writeOut?:(text:string)=>unknown}
export declare function main(argv:string[],dependencies?:CliDependencies):Promise<number>;
