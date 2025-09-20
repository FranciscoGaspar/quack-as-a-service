'use client';

import { DataTable } from '@/components/dataTable/DataTable';
import { ErrorAlert } from '@/components/ErrorAlert';
import { columns } from '@/components/factory-entries/columns';
import { useFactoryEntries } from '@/hooks/factory-entries/useFactoryEntries';
import { fuzzyFilterFn } from '@/lib/dataTable';
import { DoorOpen, Loader2 } from 'lucide-react';

const LoadingFactoryEntries = () => {
  return (
    <div className="flex items-center justify-center">
      <Loader2 className="animate-spin text-primary" size={80} />
    </div>
  );
};

const EmptyFactoryEntries = () => {
  return (
    <div className="flex flex-col gap-4 h-full items-center justify-center">
      <div className="rounded-full bg-accent w-20 h-20 flex items-center justify-center">
        <DoorOpen className="stroke-primary" size={40} />
      </div>
      <div className="flex flex-col gap-1 text-center">
        <p className="font-bold">No Factory Entries added yet</p>
        <p className="text-muted-foreground">
          Please wait until someone enters the factory.
        </p>
      </div>
    </div>
  );
};

export const FactoryEntriesComponent = () => {
  const { data: factoryEntries, isLoading } = useFactoryEntries();

  if (isLoading) {
    return <LoadingFactoryEntries />;
  }

  if (!factoryEntries) {
    return <ErrorAlert />;
  }

  if (factoryEntries.length <= 0) {
    return <EmptyFactoryEntries />;
  }

  return (
    <DataTable
      columns={columns}
      config={{
        filters: {
          search: {
            placeholder: 'Search',
            filterFn: fuzzyFilterFn(['room_name']),
          },
          filter: [
            {
              type: 'select',
              column: 'room_name',
            },
            {
              type: 'select',
              column: 'user_name',
            },
          ],
        },
      }}
      data={factoryEntries}
    />
  );
};
