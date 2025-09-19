import { PageHeader } from "@/components/PageHeader";

const HomePage = () => {
  return (
    <div className="flex flex-1 flex-col h-full">
      <PageHeader
        description="Your Quack-as-a-Service Dashboard"
        title="Dashboard"
      />
      <div className="h-full py-6">Quack-as-a-Service</div>
    </div>
  );
};

export default HomePage;
