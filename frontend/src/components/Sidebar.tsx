"use client";

import { ROUTES } from "@/constants/routes";
import {
  CameraIcon,
  ClipboardPenLineIcon,
  DoorOpenIcon,
  LayoutDashboard,
  type LucideIcon,
  MessageSquareIcon,
  PackageOpenIcon,
  Settings,
  ShieldIcon
} from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Sidebar as ShadcnSidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "./ui/sidebar";

type Route = {
  icon: LucideIcon;
  title: string;
  url: string;
};

type GroupedRoute = {
  key: string;
  label?: string;
  items: Route[];
};

const groupRoutes: GroupedRoute[] = [
  {
    key: "dashboard",
    items: [{ icon: LayoutDashboard, title: "Dashboard", url: ROUTES.home }],
  },
  {
    key: "mainMenu",
    label: "Main Menu",
    items: [
      {
        icon: DoorOpenIcon,
        title: "Factory Entries",
        url: ROUTES.factoryEntries,
      },
    ],
  },
  {
    key: "locations",
    label: "Locations",
    items: [
      {
        icon: ShieldIcon,
        title: "Production Floor",
        url: ROUTES.liveCapture("production-floor"),
      },
      {
        icon: ClipboardPenLineIcon,
        title: "Assembly Line",
        url: ROUTES.liveCapture("assembly-line"),
      },
      {
        icon: PackageOpenIcon,
        title: "Packaging Area",
        url: ROUTES.liveCapture("packaging-area"),
      },
      {
        icon: CameraIcon,
        title: "Reports",
        url: ROUTES.reports,
      },
      {
        icon: MessageSquareIcon,
        title: "Ask AI",
        url: ROUTES.aiChat,
      },
      {
        icon: Settings,
        title: "Room Configurations",
        url: ROUTES.roomConfigurations,
      },
    ],
  },
];

const isActive = (routeUrl: string, currentPath: string) => {
  if (routeUrl === "/") {
    return currentPath === "/";
  }

  return currentPath === routeUrl || currentPath.startsWith(`${routeUrl}/`);
};

export const Sidebar = () => {
  const pathname = usePathname();

  return (
    <ShadcnSidebar collapsible="icon" variant="sidebar">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton asChild size="lg">
              <Link href={ROUTES.home}>
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg text-sidebar-primary-foreground bg-gradient-to-r from-blue-500 to-blue-600">
                  <Image
                    alt=""
                    height={16}
                    src="https://quack-as-a-service-bucket.s3.us-east-1.amazonaws.com/ChatGPT+Image+Sept+19+2025+from+Team+Suggestion+(2).png"
                    width={16}
                  />
                </div>
                <div className="flex flex-col gap-0.5 leading-none">
                  <span className="font-semibold">QaaS</span>
                  <span className="">v1.0.0</span>
                </div>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        {groupRoutes.map(({ key, label, items }) => {
          return (
            <SidebarGroup key={key}>
              {label && <SidebarGroupLabel>{label}</SidebarGroupLabel>}
              <SidebarMenu className="gap-2">
                {items.map(({ icon, title, url }) => {
                  const Icon = icon;

                  return (
                    <SidebarMenuItem key={title}>
                      <SidebarMenuButton
                        asChild
                        isActive={isActive(url, pathname)}
                        tooltip={title}
                      >
                        <Link href={url}>
                          <Icon />
                          {title}
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  );
                })}
              </SidebarMenu>
            </SidebarGroup>
          );
        })}
      </SidebarContent>
      <SidebarRail />
    </ShadcnSidebar>
  );
};
