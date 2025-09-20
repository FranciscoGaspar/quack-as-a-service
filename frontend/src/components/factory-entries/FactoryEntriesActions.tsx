"use client";

import { DeleteFactoryEntryDialog } from "@/components/factory-entries/DeleteFactoryEntryDialog";
import type { FactoryEntries } from "@/services/factoryEntries.service";

type FactoryEntriesActionsProps = {
  factoryEntry: FactoryEntries;
};

export const FactoryEntriesActions = ({
  factoryEntry,
}: FactoryEntriesActionsProps) => {
  return (
    <div className="flex items-center gap-2">
      <DeleteFactoryEntryDialog factoryEntry={factoryEntry} />
    </div>
  );
};
