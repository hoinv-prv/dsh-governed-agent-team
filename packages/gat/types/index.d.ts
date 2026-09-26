export interface PackageStatus {
  readonly proposalRevision: 3;
  readonly proposalStatus: 'inactive';
  readonly implementationStatus: 'standalone-under-development';
  readonly conformanceStatus: 'not-executed';
  readonly dshRuntimeStatus: 'not-integrated';
  readonly mcpBridgeStatus: 'not-integrated';
}

export const PACKAGE_STATUS: Readonly<PackageStatus>;
