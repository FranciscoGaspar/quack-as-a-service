"use client";

import { FactoryEntriesActions } from "@/components/factory-entries/FactoryEntriesActions";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/date";
import type { FactoryEntries } from "@/services/factoryEntries.service";
import type { ColumnDef } from "@tanstack/react-table";
import { CheckCircle2, XCircle } from "lucide-react";

export const columns: ColumnDef<FactoryEntries>[] = [
  {
    accessorKey: "user_name",
    header: "User",
    size: 100,
  },
  {
    accessorKey: "room_name",
    header: "Room Name",
    cell: ({ row }) => {
      const { room_name } = row.original;
      return (
        <span className="capitalize">{room_name.replaceAll("-", " ")}</span>
      );
    },
    size: 100,
  },
  {
    accessorKey: "approval_status",
    header: "Status",
    cell: ({ row }) => {
      const { is_approved, equipment } = row.original;

      const presentEquipment = Object.values(equipment).filter(Boolean).length;
      const requiredEquipment = Object.entries(equipment).length;

      return (
        <div className="flex flex-col gap-1">
          <Badge
            className="flex items-center gap-1 w-fit"
            variant={is_approved ? "default" : "destructive"}
          >
            {is_approved ? <CheckCircle2 /> : <XCircle />}
            {is_approved ? "Approved" : "Denied"}
          </Badge>
          <div className="text-xs text-muted-foreground">
            Equipment: {presentEquipment} / {requiredEquipment}
          </div>
        </div>
      );
    },
    size: 100,
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
      return <FactoryEntriesActions factoryEntry={factoryEntry} />;
    },
  },
];
