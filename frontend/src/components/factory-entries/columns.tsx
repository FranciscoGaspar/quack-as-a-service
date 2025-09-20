"use client";

import { FactoryEntriesActions } from "@/components/factory-entries/FactoryEntriesActions";
import { formatDate } from "@/lib/date";
import type { FactoryEntries } from "@/services/factoryEntries.service";
import type { ColumnDef } from "@tanstack/react-table";
import { CheckCircle2 } from "lucide-react";

export const createColumns = (onViewCompliance: (entry: FactoryEntries) => void): ColumnDef<FactoryEntries>[] => [
  {
    accessorKey: "user_id",
    header: "User",
    size: 50,
  },
  {
    accessorKey: "room_name",
    header: "Room Name",
  },
  {
    accessorKey: "equipment",
    header: "Equipment",
    cell: ({ row }) => {
      const { equipment } = row.original;

      const equipedEquipment = Object.values(equipment).filter(Boolean).length;
      const equipmentCount = Object.entries(equipment).length;

      return (
        <div className="flex items-center gap-2">
          {equipedEquipment}/{equipmentCount}
          <CheckCircle2 size={14} />
        </div>
      );
    },
  },
  {
    accessorKey: "entered_at",
    header: "Entered At",
    cell: ({ row }) => {
      const { entered_at } = row.original;
      return formatDate(entered_at);
    },
  },
  {
    accessorKey: "actions",
    header: "Actions",
    size: 50,
    cell: ({ row }) => {
      const factoryEntry = row.original;
      return <FactoryEntriesActions factoryEntry={factoryEntry} onViewCompliance={onViewCompliance} />;
    },
  },
];
