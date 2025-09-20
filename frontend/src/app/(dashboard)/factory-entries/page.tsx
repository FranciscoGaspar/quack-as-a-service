import { FactoryEntriesComponent } from "@/components/factory-entries/FactoryEntries";
import { PageHeader } from "@/components/PageHeader";

const FactoryEntriesPage = async () => {
  return (
    <div className="flex flex-1 flex-col h-full">
      <div className="flex justify-between">
        <PageHeader
          description="Factory Entries overview"
          title="Factory Entries"
        />
      </div>
      <div className="h-full py-6">
        <FactoryEntriesComponent />
      </div>
    </div>
  );
};

export default FactoryEntriesPage;
