'use client';

import { FactoryEntriesActions } from '@/components/factory-entries/FactoryEntriesActions';
import { Badge } from '@/components/ui/badge';
import { formatDate } from '@/lib/date';
import type { FactoryEntries } from '@/services/factoryEntries.service';
import type { ColumnDef } from '@tanstack/react-table';
import { CheckCircle2, XCircle, Clock, Shield } from 'lucide-react';

export const columns: ColumnDef<FactoryEntries>[] = [
  {
    accessorKey: 'user_name',
    header: 'User',
  },
  {
    accessorKey: 'room_name',
    header: 'Room Name',
    cell: ({ row }) => {
      const { room_name } = row.original;
      return (
        <span className="capitalize">{room_name.replaceAll('-', ' ')}</span>
      );
    },
  },
  {
    accessorKey: 'equipment',
    header: 'Equipment',
    cell: ({ row }) => {
      const { equipment } = row.original;

      const presentItems = Object.entries(equipment)
        .filter(([_, isPresent]) => isPresent)
        .map(([item, _]) => item);
      
      const missingItems = Object.entries(equipment)
        .filter(([_, isPresent]) => !isPresent)
        .map(([item, _]) => item);

      return (
        <div className="flex flex-col gap-1">
          {presentItems.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {presentItems.map(item => (
                <span key={item} className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded capitalize">
                  ✓ {item}
                </span>
              ))}
            </div>
          )}
          {missingItems.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {missingItems.map(item => (
                <span key={item} className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded capitalize">
                  ✗ {item}
                </span>
              ))}
            </div>
          )}
        </div>
      );
    },
    size: 200,
  },
  {
    accessorKey: 'approval_status',
    header: 'Status',
    cell: ({ row }) => {
      const { is_approved, equipment_score, approval_reason } = row.original;
      
      // Determine status display
      let variant: "default" | "destructive" | "outline" | "secondary" = "secondary";
      let icon = <Clock className="w-3 h-3" />;
      let text = "Pending";
      
      if (is_approved === true) {
        variant = "default";
        icon = <CheckCircle2 className="w-3 h-3" />;
        text = "Approved";
      } else if (is_approved === false) {
        variant = "destructive"; 
        icon = <XCircle className="w-3 h-3" />;
        text = "Denied";
      }
      
      // No more score display - just simple APPROVED/DENIED
      
      return (
        <div className="flex flex-col gap-1">
          <Badge variant={variant} className="flex items-center gap-1 w-fit">
            {icon}
            {text}
          </Badge>
          {approval_reason && (
            <span className="text-xs text-muted-foreground max-w-[200px] leading-relaxed" 
                  title={approval_reason}>
              {is_approved === true ? 'All required items present' : 
               is_approved === false ? `Missing required items` : 
               'Processing...'}
            </span>
          )}
        </div>
      );
    },
    size: 200,
  },
  {
    accessorKey: 'entered_at',
    header: 'Entered At',
    cell: ({ row }) => {
      const { entered_at } = row.original;
      return formatDate(entered_at);
    },
  },
  {
    accessorKey: 'actions',
    header: 'Actions',
    size: 50,
    cell: ({ row }) => {
      const factoryEntry = row.original;
      return <FactoryEntriesActions factoryEntry={factoryEntry} />;
    },
  },
];
