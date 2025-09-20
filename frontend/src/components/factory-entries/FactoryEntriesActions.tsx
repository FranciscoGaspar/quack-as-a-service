"use client";

import { DeleteFactoryEntryDialog } from "@/components/factory-entries/DeleteFactoryEntryDialog";
import { Button } from "@/components/ui/button";
import type { FactoryEntries } from "@/services/factoryEntries.service";
import { Eye } from "lucide-react";

type FactoryEntriesActionsProps = {
  factoryEntry: FactoryEntries;
  onViewCompliance: (entry: FactoryEntries) => void;
};

export const FactoryEntriesActions = ({
  factoryEntry,
  onViewCompliance,
}: FactoryEntriesActionsProps) => {
  return (
    <div className="flex items-center gap-2">
      <Button
        size="icon"
        variant="outline"
        onClick={() => onViewCompliance(factoryEntry)}
        title="View Equipment Compliance"
      >
        <Eye className="h-4 w-4" />
      </Button>
      <DeleteFactoryEntryDialog factoryEntry={factoryEntry} />
    </div>
  );
};
