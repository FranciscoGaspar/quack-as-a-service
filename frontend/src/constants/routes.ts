export const ROUTES = {
  home: "/",

  factoryEntries: "/factory-entries",
  liveCapture: (id: string) => `/${id}/live-capture`,
  reports: "/reports",
  aiChat: "/ai-chat",
  roomConfigurations: "/room-configurations",
  accidents: "/accidents",
} as const;
