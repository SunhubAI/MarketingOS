create extension if not exists "pgcrypto";

create table if not exists template_packs (
  id uuid primary key default gen_random_uuid(),
  name text unique not null,
  required_sizes text[] not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists templates (
  id uuid primary key default gen_random_uuid(),
  template_name text not null,
  template_type text not null check (template_type in ('PRODUCT','BLOG','CAMPAIGN','PARTNER','EVENT')),
  pack_id uuid not null references template_packs(id) on delete cascade,
  size text not null check (size in ('IG_4x5','LINKEDIN_1x1','STORY_9x16','BANNER_1400x170')),
  version int not null,
  status text not null check (status in ('DRAFT','APPROVED','REJECTED','ARCHIVED')) default 'DRAFT',
  is_active boolean not null default false,
  figma_file_key text not null,
  figma_node_id text not null,
  detected_placeholders jsonb not null default '[]'::jsonb,
  validation_report jsonb not null default '{}'::jsonb,
  preview_image_url text,
  created_by uuid not null,
  approved_by uuid,
  approved_at timestamptz,
  rejected_reason text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (pack_id, size, version)
);

create unique index if not exists idx_templates_single_active
on templates (pack_id, size)
where is_active = true;

create table if not exists bulk_jobs (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  pack_id uuid not null references template_packs(id),
  created_by uuid not null,
  status text not null check (status in ('DRAFT','PROCESSING','COMPLETED','FAILED')) default 'DRAFT',
  created_at timestamptz not null default now(),
  completed_at timestamptz
);

create table if not exists bulk_job_rows (
  id uuid primary key default gen_random_uuid(),
  job_id uuid not null references bulk_jobs(id) on delete cascade,
  row_index int not null,
  mapped_data jsonb not null,
  validation_status text not null check (validation_status in ('VALID','INVALID')),
  validation_errors jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists bulk_job_mappings (
  job_id uuid primary key references bulk_jobs(id) on delete cascade,
  mapping jsonb not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists bulk_job_outputs (
  id uuid primary key default gen_random_uuid(),
  job_id uuid not null references bulk_jobs(id) on delete cascade,
  row_id uuid not null references bulk_job_rows(id) on delete cascade,
  template_id uuid not null references templates(id),
  size text not null,
  asset_url text,
  created_at timestamptz not null default now()
);

create or replace function activate_template(template_uuid uuid)
returns void
language plpgsql
as $$
declare
  v_pack_id uuid;
  v_size text;
  v_status text;
begin
  select pack_id, size, status
    into v_pack_id, v_size, v_status
  from templates
  where id = template_uuid
  for update;

  if v_pack_id is null then
    raise exception 'Template % not found', template_uuid;
  end if;

  if v_status <> 'APPROVED' then
    raise exception 'Template % is not APPROVED', template_uuid;
  end if;

  update templates
    set is_active = false,
        updated_at = now()
  where pack_id = v_pack_id
    and size = v_size
    and is_active = true;

  update templates
    set is_active = true,
        updated_at = now()
  where id = template_uuid;
end;
$$;
