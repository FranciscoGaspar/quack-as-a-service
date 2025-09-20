export const ROUTES = {
  home: "/",

  factoryEntries: "/factory-entries",
  liveCapture: (id: string) => `/${id}/live-capture`,
} as const;
