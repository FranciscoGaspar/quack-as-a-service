import { toast as sonnerToast } from "sonner";

export interface ToastProps {
  title?: string;
  description?: string;
  variant?: "default" | "destructive";
}

export const useToast = () => {
  const toast = ({ title, description, variant = "default" }: ToastProps) => {
    const message = title || "";
    const desc = description || "";

    if (variant === "destructive") {
      sonnerToast.error(message, {
        description: desc,
      });
    } else {
      sonnerToast.success(message, {
        description: desc,
      });
    }
  };

  return { toast };
};
