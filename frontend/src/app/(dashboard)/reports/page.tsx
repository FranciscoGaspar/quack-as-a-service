import { PageHeader } from "@/components/PageHeader";
import { ReportsComponent } from "@/components/reports/ReportComponents";

const ReportsPage = async () => {
  return (
    <div className="flex flex-1 flex-col h-full">
      <div className="flex justify-between">
        <PageHeader
          description="Analytics and insights for equipment compliance tracking"
          title="Compliance Reports"
        />
      </div>
      <div className="h-full py-6">
        <ReportsComponent />
      </div>
    </div>
  );
};

export default ReportsPage;
