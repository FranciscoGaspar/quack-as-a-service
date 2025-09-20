"use client";

import { DataTable } from "@/components/dataTable/DataTable";
import { ErrorAlert } from "@/components/ErrorAlert";
import { createColumns } from "@/components/factory-entries/columns";
import { EquipmentComplianceDisplay } from "@/components/live-capture/EquipmentComplianceDisplay";
import { useFactoryEntries } from "@/hooks/factory-entries/useFactoryEntries";
import type { FactoryEntries } from "@/services/factoryEntries.service";
import { useState } from "react";

const LoadingFactoryEntries = () => {
  return <div>Loading Factory Entries</div>;
};

const EmptyFactoryEntries = () => {
  return <div>No Factory Entries Available</div>;
};

export const FactoryEntriesComponent = () => {
  const { data: factoryEntries, isLoading } = useFactoryEntries();
  const [selectedEntry, setSelectedEntry] = useState<FactoryEntries | null>(null);
  const [showComplianceDialog, setShowComplianceDialog] = useState(false);

  const handleViewCompliance = (entry: FactoryEntries) => {
    setSelectedEntry(entry);
    setShowComplianceDialog(true);
  };

  if (isLoading) {
    return <LoadingFactoryEntries />;
  }

  if (!factoryEntries) {
    return <ErrorAlert />;
  }

  if (factoryEntries.length <= 0) {
    return <EmptyFactoryEntries />;
  }

  return (
    <>
      <DataTable 
        columns={createColumns(handleViewCompliance)} 
        data={factoryEntries} 
      />
      {selectedEntry && (
        <EquipmentComplianceDisplay
          complianceData={selectedEntry}
          showComplianceDialog={showComplianceDialog}
          setShowComplianceDialog={setShowComplianceDialog}
        />
      )}
    </>
  );
};
