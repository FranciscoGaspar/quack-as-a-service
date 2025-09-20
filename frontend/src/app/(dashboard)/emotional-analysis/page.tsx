import { PageHeader } from "@/components/PageHeader";
import { EmotionalAnalysisComponent } from "@/components/emotial-analysis/EmotionalAnalysisComponent";

const EmotionalAnalysisPage = async () => {
  return (
    <div className="flex flex-1 flex-col h-full">
      <div className="flex justify-between">
        <PageHeader
          description="Emotional analysis overview"
          title="Emotional Analysis"
        />
      </div>
      <div className="h-full py-6">
        <EmotionalAnalysisComponent />
      </div>
    </div>
  );
};

export default EmotionalAnalysisPage;
