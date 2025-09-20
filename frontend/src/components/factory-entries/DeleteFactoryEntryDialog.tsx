import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Button, buttonVariants } from "@/components/ui/button";
import { useDeleteFactoryEntry } from "@/hooks/factory-entries/useDeleteFactoryEntry";
import type { FactoryEntries } from "@/services/factoryEntries.service";
import { Trash2 } from "lucide-react";

type DeleteFactoryEntryDialogProps = {
  factoryEntry: FactoryEntries;
};

export const DeleteFactoryEntryDialog = ({
  factoryEntry,
}: DeleteFactoryEntryDialogProps) => {
  const { isPending, mutate } = useDeleteFactoryEntry(factoryEntry.id);

  const handleDeleteFactoryEntry = () => {
    mutate();
  };

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button size="icon" variant="destructive">
          <Trash2 />
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
          <AlertDialogDescription>
            This will permanently delete this factory entry. This action cannot
            be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction
            className={buttonVariants({ variant: "destructive" })}
            disabled={isPending}
            onClick={handleDeleteFactoryEntry}
          >
            Delete
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};
