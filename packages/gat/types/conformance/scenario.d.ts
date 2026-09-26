import type{ConformanceDispatch}from'./index.d.ts';
export interface ScenarioStep{readonly target:'partition'|'policy'|'selector'|'memory'|'adapter';readonly method:string;readonly args?:Readonly<Record<string,unknown>>}
export interface ScenarioAssertion{readonly path:string;readonly op:'equals'|'absent'|'includes'|'truthy';readonly value?:unknown}
export interface ScenarioDefinition{readonly environment?:Readonly<Record<string,unknown>>;readonly steps:ReadonlyArray<ScenarioStep>;readonly assertions:ReadonlyArray<ScenarioAssertion>;readonly bindings:Readonly<Record<string,unknown>>}
export interface ScenarioFixture{readonly format:'gat-conformance-scenario-fixture/1';readonly scenarios:Readonly<Record<string,ScenarioDefinition>>}
export declare function createPackageScenarioHandlers(fixture:ScenarioFixture,options?:{now?:()=>number;deadlineMs?:number}):Record<string,ConformanceDispatch>;
