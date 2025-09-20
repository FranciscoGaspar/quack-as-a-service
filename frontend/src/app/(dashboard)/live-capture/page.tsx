import { LiveCapture } from "@/components/live-capture/LiveCapture";
import { PageHeader } from "@/components/PageHeader";

const LiveCapturePage = async () => { 
  return (
    <div className="flex flex-1 flex-col h-full">
      <div className="flex justify-between">
        <PageHeader
          description="Live Capture overview"
          title="Live Capture"
        />
      </div>
      <div className="h-full py-6">
        <LiveCapture />
      </div>
    </div>
  );
};

export default LiveCapturePage;
