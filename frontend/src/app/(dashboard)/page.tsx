import { PageHeader } from "@/components/PageHeader";
import Image from "next/image";

const HomePage = () => {
  return (
    <div className="flex flex-1 flex-col h-full">
      <PageHeader
        description="Your Quack-as-a-Service Dashboard"
        title="Dashboard"
      />
      <div className="h-full py-6">
        <Image
          alt=""
          height={800}
          src="https://quack-as-a-service-bucket.s3.us-east-1.amazonaws.com/gloves.jpg"
          width={800}
        />
      </div>
    </div>
  );
};

export default HomePage;
