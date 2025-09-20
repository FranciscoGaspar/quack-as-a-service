"use client";

import { DeleteFactoryEntryDialog } from "@/components/factory-entries/DeleteFactoryEntryDialog";
import { EquipmentComplianceDisplay } from "@/components/live-capture/EquipmentComplianceDisplay";
import { Button } from "@/components/ui/button";
import type { FactoryEntries } from "@/services/factoryEntries.service";
import { Eye } from "lucide-react";
import { useState } from "react";

type FactoryEntriesActionsProps = {
  factoryEntry: FactoryEntries;
};

export const FactoryEntriesActions = ({
  factoryEntry,
}: FactoryEntriesActionsProps) => {
  const [showComplianceDialog, setShowComplianceDialog] = useState(false);

  return (
    <>
      {showComplianceDialog && (
        <EquipmentComplianceDisplay
          complianceData={factoryEntry}
          setShowComplianceDialog={setShowComplianceDialog}
          showComplianceDialog={showComplianceDialog}
        />
      )}
      <div className="flex items-center gap-2">
        <Button
          onClick={() => setShowComplianceDialog(true)}
          size="icon"
          title="View Equipment Compliance"
          variant="outline"
        >
          <Eye />
        </Button>
        <DeleteFactoryEntryDialog factoryEntry={factoryEntry} />
      </div>
    </>
  );
};
