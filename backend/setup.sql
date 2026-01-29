CREATE TABLE users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  org_id UUID
);

CREATE TABLE events (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID,
  org_id UUID,
  data_type TEXT,
  action TEXT,
  domain TEXT,
  created_at TIMESTAMP DEFAULT now()
);
