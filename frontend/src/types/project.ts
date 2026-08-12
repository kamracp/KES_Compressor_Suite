export type Project = {
  id: number;
  organization_id: number;
  project_code: string;
  project_name: string;
  client_name: string | null;
  plant_name: string | null;
  location: string | null;
  service_description: string | null;
  status: string;
  created_at: string;
  updated_at: string;
};

export type ProjectCreateRequest = {
  project_code: string;
  project_name: string;
  client_name?: string | null;
  plant_name?: string | null;
  location?: string | null;
  service_description?: string | null;
  status?: string;
};
