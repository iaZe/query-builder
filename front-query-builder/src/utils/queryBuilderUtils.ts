export const mapDefinitionsToOptions = (
  definitions: Record<string, { label: string }>,
) => {
  return Object.entries(definitions).map(([key, value]) => ({
    value: key,
    label: value.label,
  }));
};
