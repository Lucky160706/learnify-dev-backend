-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Courses Table
create table public.courses (
  id uuid default uuid_generate_v4() primary key,
  title text not null,
  slug text not null unique,
  description text,
  small_description text,
  cover_image text not null,
  status text not null default 'Draft',
  file_key text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Chapters Table
create table public.chapters (
  id uuid default uuid_generate_v4() primary key,
  course_id uuid references public.courses(id) on delete cascade not null,
  title text not null,
  slug text not null,
  position integer not null default 0,
  status text default 'Draft',
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
  unique(course_id, slug)
);

-- Lessons Table
create table public.lessons (
  id uuid default uuid_generate_v4() primary key,
  chapter_id uuid references public.chapters(id) on delete cascade not null,
  title text not null,
  slug text not null unique,
  label text,
  type text not null, -- Theory, Video, Assignment, Quiz
  author_name text,
  published_at date,
  position integer not null default 0,
  status text default 'Draft',
  mdx_path text, -- Maps to fileKey
  video_key text,
  thumbnail_key text,
  views integer default 0,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable Row Level Security (RLS) - Optional but recommended
alter table public.courses enable row level security;
alter table public.chapters enable row level security;
alter table public.lessons enable row level security;

-- Create policies to allow public access (Adjust for production!)
create policy "Allow public read access" on public.courses for select using (true);
create policy "Allow public insert access" on public.courses for insert with check (true);
create policy "Allow public update access" on public.courses for update using (true);
create policy "Allow public delete access" on public.courses for delete using (true);

create policy "Allow public read access" on public.chapters for select using (true);
create policy "Allow public insert access" on public.chapters for insert with check (true);
create policy "Allow public update access" on public.chapters for update using (true);
create policy "Allow public delete access" on public.chapters for delete using (true);

create policy "Allow public read access" on public.lessons for select using (true);
create policy "Allow public insert access" on public.lessons for insert with check (true);
create policy "Allow public update access" on public.lessons for update using (true);
create policy "Allow public delete access" on public.lessons for delete using (true);
