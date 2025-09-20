import { ChatComponent } from "@/components/ai-chat/AIChatComponent";
import { PageHeader } from "@/components/PageHeader";

const ChatPage = async () => {
  return (
    <div className="flex flex-1 flex-col h-full">
      <div className="flex justify-between">
        <PageHeader
          description="Chat overview"
          title="Chat"
        />
      </div>
      <div className="h-full py-6">
        <ChatComponent />
      </div>
    </div>
  );
};

export default ChatPage;
