"use client";

import { ErrorAlert } from "@/components/ErrorAlert";
import { useFactoryEntries } from "@/hooks/factory-entries/useFactoryEntries";

const LoadingFactoryEntries = () => {
  return <div>Loading Factory Entries</div>;
};

const EmptyFactoryEntries = () => {
  return <div>No Factory Entries Available</div>;
};

export const FactoryEntries = () => {
  const { data: factoryEntries, isLoading } = useFactoryEntries();

  if (isLoading) {
    return <LoadingFactoryEntries />;
  }

  if (!factoryEntries) {
    return <ErrorAlert />;
  }

  if (factoryEntries.length <= 0) {
    return <EmptyFactoryEntries />;
  }

  return <pre>{JSON.stringify(factoryEntries, null, 4)}</pre>;
};
