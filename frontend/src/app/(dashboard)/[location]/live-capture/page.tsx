import { LiveCapture } from "@/components/live-capture/LiveCapture";
import { PageHeader } from "@/components/PageHeader";

type LiveCapturePageProps = {
  params: Promise<{ location: string }>;
};

const LiveCapturePage = async ({ params }: LiveCapturePageProps) => {
  const { location } = await params;
  const cleanLocation = location.replaceAll("-", " ");

  return (
    <div className="flex flex-1 flex-col h-full">
      <div className="flex justify-between">
        <PageHeader
          description="Live Capture overview"
          title={`Location: ${cleanLocation}`}
        />
      </div>
      <div className="h-full py-6">
        <LiveCapture location={location} />
      </div>
    </div>
  );
};

export default LiveCapturePage;
