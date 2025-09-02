-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table (extends auth.users)
CREATE TABLE public.users (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create words table
CREATE TABLE public.words (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  word TEXT NOT NULL,
  chinese_meaning TEXT NOT NULL,
  english_meaning TEXT,
  phonetic TEXT,
  example_sentence TEXT,
  synonyms TEXT[],
  antonyms TEXT[],
  difficulty_level INTEGER DEFAULT 1 CHECK (difficulty_level >= 1 AND difficulty_level <= 5),
  review_count INTEGER DEFAULT 0,
  last_reviewed TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT unique_user_word UNIQUE(user_id, word)
);

-- Create review_sessions table
CREATE TABLE public.review_sessions (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  words_reviewed INTEGER NOT NULL DEFAULT 0,
  difficult_words UUID[],
  session_time INTEGER NOT NULL DEFAULT 0, -- in seconds
  session_type TEXT NOT NULL DEFAULT 'random', -- 'random', 'difficult', 'recent'
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_words_user_id ON public.words(user_id);
CREATE INDEX idx_words_created_at ON public.words(created_at DESC);
CREATE INDEX idx_words_difficulty ON public.words(difficulty_level);
CREATE INDEX idx_words_last_reviewed ON public.words(last_reviewed);
CREATE INDEX idx_words_word_search ON public.words USING gin(to_tsvector('english', word));
CREATE INDEX idx_words_meaning_search ON public.words USING gin(to_tsvector('chinese', chinese_meaning));

CREATE INDEX idx_review_sessions_user_id ON public.review_sessions(user_id);
CREATE INDEX idx_review_sessions_created_at ON public.review_sessions(created_at DESC);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at 
  BEFORE UPDATE ON public.users 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_words_updated_at 
  BEFORE UPDATE ON public.words 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to get random words
CREATE OR REPLACE FUNCTION get_random_words(user_id_param UUID, limit_param INTEGER DEFAULT 20)
RETURNS SETOF public.words AS $$
BEGIN
  RETURN QUERY
  SELECT * FROM public.words 
  WHERE user_id = user_id_param 
  ORDER BY RANDOM() 
  LIMIT limit_param;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to handle user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email)
  VALUES (NEW.id, NEW.email);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for new user creation
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Row Level Security (RLS) policies
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.words ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.review_sessions ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "Users can view own profile" ON public.users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.users
  FOR UPDATE USING (auth.uid() = id);

-- Words policies
CREATE POLICY "Users can view own words" ON public.words
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own words" ON public.words
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own words" ON public.words
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own words" ON public.words
  FOR DELETE USING (auth.uid() = user_id);

-- Review sessions policies
CREATE POLICY "Users can view own review sessions" ON public.review_sessions
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own review sessions" ON public.review_sessions
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON public.users TO authenticated;
GRANT ALL ON public.words TO authenticated;
GRANT ALL ON public.review_sessions TO authenticated;
GRANT EXECUTE ON FUNCTION get_random_words TO authenticated;