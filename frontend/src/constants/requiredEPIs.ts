export const getRequiredEPIs = (location: string) => {
  switch (location) {
    case "production-floor":
      return ["Mask", "Gloves", "Hair Net"];
    case "assembly-line":
      return ["Gloves", "Hair Net"];
    case "packaging-area":
      return ["Gloves"];
    default:
      return [];
  }
};
