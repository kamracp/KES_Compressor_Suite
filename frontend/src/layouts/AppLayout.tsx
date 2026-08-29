import type { PropsWithChildren } from "react";

import {
  ClipboardCheck,
  FileText,
  FolderKanban,
  LayoutDashboard,
  LogOut,
  Menu,
  ShieldCheck,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { NavLink } from "react-router";

import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { cn } from "@/lib/utils";

import { useAuth } from "../features/auth/AuthProvider";

type NavigationItem = {
  to: string;
  label: string;
  icon: LucideIcon;
  end?: boolean;
};

const navigationItems: NavigationItem[] = [
  {
    to: "/",
    label: "Dashboard",
    icon: LayoutDashboard,
    end: true,
  },
  {
    to: "/projects",
    label: "Projects",
    icon: FolderKanban,
  },
  {
    to: "/assessments",
    label: "Assessments",
    icon: ClipboardCheck,
  },
  {
    to: "/reports",
    label: "Reports",
    icon: FileText,
  },
];

function navigationLinkClassName({
  isActive,
}: {
  isActive: boolean;
}) {
  return cn(
    "group flex min-h-11 items-center gap-3 rounded-lg px-3 py-2.5",
    "text-sm font-medium transition-colors",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400",
    isActive
      ? "bg-white/12 text-white shadow-sm"
      : "text-slate-300 hover:bg-white/8 hover:text-white",
  );
}

function DesktopNavigation() {
  return (
    <nav
      className="space-y-1"
      aria-label="Primary navigation"
    >
      {navigationItems.map((item) => {
        const Icon = item.icon;

        return (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={navigationLinkClassName}
          >
            <Icon className="size-4.5 text-slate-400 transition-colors group-hover:text-white" />

            <span>{item.label}</span>
          </NavLink>
        );
      })}
    </nav>
  );
}

function MobileNavigation() {
  return (
    <nav
      className="space-y-1"
      aria-label="Mobile navigation"
    >
      {navigationItems.map((item) => {
        const Icon = item.icon;

        return (
          <SheetClose
            key={item.to}
            asChild
          >
            <NavLink
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                cn(
                  "flex min-h-11 items-center gap-3 rounded-lg px-3 py-2.5",
                  "text-sm font-medium transition-colors",
                  isActive
                    ? "bg-slate-100 text-slate-950"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-950",
                )
              }
            >
              <Icon className="size-4.5" />
              <span>{item.label}</span>
            </NavLink>
          </SheetClose>
        );
      })}
    </nav>
  );
}

export function AppLayout({
  children,
}: PropsWithChildren) {
  const {
    currentUser,
    logout,
  } = useAuth();

  const displayName =
    currentUser?.full_name?.trim() ||
    currentUser?.email ||
    "KES User";

  const organizationLabel =
    currentUser?.organization_id != null
      ? `Organization ${currentUser.organization_id}`
      : "Organization unavailable";

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950">
      <div className="flex min-h-screen">
        <aside className="hidden w-72 shrink-0 flex-col border-r border-slate-800 bg-slate-950 lg:flex">
          <div className="flex h-20 items-center gap-3 border-b border-white/8 px-5">
            <div className="grid size-11 place-items-center rounded-xl bg-white text-xs font-black tracking-[0.14em] text-slate-950 shadow-sm">
              KES
            </div>

            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-white">
                Compressor Suite
              </p>

              <p className="mt-0.5 text-xs text-slate-400">
                Engineering Platform
              </p>
            </div>
          </div>

          <div className="flex-1 px-4 py-6">
            <div className="mb-3 px-3">
              <p className="text-[11px] font-bold tracking-[0.16em] text-slate-500 uppercase">
                Workspace
              </p>
            </div>

            <DesktopNavigation />
          </div>

          <div className="border-t border-white/8 p-4">
            <div className="mb-3 flex items-center gap-3 rounded-xl bg-white/5 p-3">
              <div className="grid size-10 shrink-0 place-items-center rounded-full bg-sky-100 text-sm font-bold text-sky-900">
                {displayName.charAt(0).toUpperCase()}
              </div>

              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-white">
                  {displayName}
                </p>

                <p className="mt-0.5 truncate text-xs text-slate-400">
                  {organizationLabel}
                </p>
              </div>
            </div>

            <Button
              type="button"
              variant="ghost"
              className="w-full justify-start text-slate-300 hover:bg-white/8 hover:text-white"
              onClick={logout}
            >
              <LogOut className="size-4" />
              Sign out
            </Button>
          </div>
        </aside>

        <div className="min-w-0 flex-1">
          <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur sm:px-6 lg:px-8">
            <div className="flex min-w-0 items-center gap-3">
              <Sheet>
                <SheetTrigger asChild>
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    className="lg:hidden"
                    aria-label="Open navigation"
                  >
                    <Menu className="size-4.5" />
                  </Button>
                </SheetTrigger>

                <SheetContent
                  side="left"
                  className="w-[300px] p-0 sm:max-w-[320px]"
                >
                  <SheetHeader className="border-b border-slate-200 px-5 py-5 text-left">
                    <div className="flex items-center gap-3">
                      <div className="grid size-10 place-items-center rounded-xl bg-slate-950 text-xs font-black tracking-[0.14em] text-white">
                        KES
                      </div>

                      <div>
                        <SheetTitle>
                          Compressor Suite
                        </SheetTitle>

                        <SheetDescription>
                          Engineering Platform
                        </SheetDescription>
                      </div>
                    </div>
                  </SheetHeader>

                  <div className="flex flex-1 flex-col px-4 py-5">
                    <p className="mb-3 px-3 text-[11px] font-bold tracking-[0.16em] text-slate-400 uppercase">
                      Workspace
                    </p>

                    <MobileNavigation />

                    <div className="mt-auto border-t border-slate-200 pt-4">
                      <div className="mb-3 px-3">
                        <p className="truncate text-sm font-semibold text-slate-900">
                          {displayName}
                        </p>

                        <p className="mt-1 truncate text-xs text-slate-500">
                          {organizationLabel}
                        </p>
                      </div>

                      <SheetClose asChild>
                        <Button
                          type="button"
                          variant="outline"
                          className="w-full justify-start"
                          onClick={logout}
                        >
                          <LogOut className="size-4" />
                          Sign out
                        </Button>
                      </SheetClose>
                    </div>
                  </div>
                </SheetContent>
              </Sheet>

              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-slate-900">
                  Engineering Workspace
                </p>

                <p className="hidden text-xs text-slate-500 sm:block">
                  Kamra Compressor OS
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700">
              <ShieldCheck className="size-3.5" />
              <span className="hidden sm:inline">
                Secure workspace
              </span>
              <span className="sm:hidden">
                Secure
              </span>
            </div>
          </header>

          <main className="mx-auto w-full max-w-[1600px] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
