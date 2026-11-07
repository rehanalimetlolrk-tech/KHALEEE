-- KHALEEE database schema
-- Run this entire file in Supabase Dashboard -> SQL Editor.
-- This starter supports accounts, public usernames, and one-to-one text conversations.

create table if not exists public.profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    username text unique not null,
    display_name text not null default 'KHALEEE member',
    created_at timestamptz not null default now()
);

create table if not exists public.conversations (
    id uuid primary key default gen_random_uuid(),
    created_by uuid not null references auth.users(id) on delete cascade,
    is_group boolean not null default false,
    name text,
    created_at timestamptz not null default now()
);

create table if not exists public.conversation_members (
    conversation_id uuid not null references public.conversations(id) on delete cascade,
    user_id uuid not null references auth.users(id) on delete cascade,
    joined_at timestamptz not null default now(),
    primary key (conversation_id, user_id)
);

create table if not exists public.messages (
    id bigint generated always as identity primary key,
    conversation_id uuid not null references public.conversations(id) on delete cascade,
    sender_id uuid not null references auth.users(id) on delete cascade,
    body text not null check (char_length(body) between 1 and 5000),
    created_at timestamptz not null default now()
);

create index if not exists idx_members_user on public.conversation_members(user_id);
create index if not exists idx_messages_conversation_created on public.messages(conversation_id, created_at);

-- Create a profile automatically when someone signs up.
create or replace function public.handle_new_khaleee_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  insert into public.profiles (id, username, display_name)
  values (
    new.id,
    lower(coalesce(new.raw_user_meta_data ->> 'username', 'user_' || substr(new.id::text, 1, 8))),
    coalesce(new.raw_user_meta_data ->> 'display_name', 'KHALEEE member')
  );
  return new;
end;
$$;

drop trigger if exists on_auth_user_created_khaleee on auth.users;
create trigger on_auth_user_created_khaleee
after insert on auth.users
for each row execute procedure public.handle_new_khaleee_user();

-- Enable Row Level Security on every exposed table.
alter table public.profiles enable row level security;
alter table public.conversations enable row level security;
alter table public.conversation_members enable row level security;
alter table public.messages enable row level security;

-- Profiles: authenticated users can discover usernames/display names.
drop policy if exists "profiles_select_authenticated" on public.profiles;
create policy "profiles_select_authenticated"
on public.profiles for select to authenticated
using (true);

drop policy if exists "profiles_update_own" on public.profiles;
create policy "profiles_update_own"
on public.profiles for update to authenticated
using (id = (select auth.uid()))
with check (id = (select auth.uid()));

-- Helper functions use SECURITY DEFINER so policies can safely check membership
-- without recursively invoking the conversation_members RLS policy.
create or replace function public.is_khaleee_member(p_conversation_id uuid)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (
    select 1
    from public.conversation_members cm
    where cm.conversation_id = p_conversation_id
      and cm.user_id = (select auth.uid())
  );
$$;

create or replace function public.is_khaleee_creator(p_conversation_id uuid)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (
    select 1
    from public.conversations c
    where c.id = p_conversation_id
      and c.created_by = (select auth.uid())
  );
$$;

-- Conversations: only members can read; creator can create.
drop policy if exists "conversation_members_read_conversation" on public.conversations;
create policy "conversation_members_read_conversation"
on public.conversations for select to authenticated
using (public.is_khaleee_member(id));

drop policy if exists "creator_can_create_conversation" on public.conversations;
create policy "creator_can_create_conversation"
on public.conversations for insert to authenticated
with check (created_by = (select auth.uid()));

-- Members: a member can see the member list for conversations they belong to.
drop policy if exists "members_can_view_chat_members" on public.conversation_members;
create policy "members_can_view_chat_members"
on public.conversation_members for select to authenticated
using (public.is_khaleee_member(conversation_id));

-- Only the conversation creator can add members, including themselves.
drop policy if exists "creator_adds_chat_members" on public.conversation_members;
create policy "creator_adds_chat_members"
on public.conversation_members for insert to authenticated
with check (public.is_khaleee_creator(conversation_id));

-- Messages: only conversation members can read or send.
drop policy if exists "members_read_messages" on public.messages;
create policy "members_read_messages"
on public.messages for select to authenticated
using (public.is_khaleee_member(conversation_id));

drop policy if exists "members_send_messages_as_themselves" on public.messages;
create policy "members_send_messages_as_themselves"
on public.messages for insert to authenticated
with check (
  sender_id = (select auth.uid())
  and public.is_khaleee_member(conversation_id)
);

-- Do not add a service-role key to Streamlit secrets or GitHub.
