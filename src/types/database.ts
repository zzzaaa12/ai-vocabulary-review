export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          email: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          email: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          email?: string
          created_at?: string
          updated_at?: string
        }
      }
      words: {
        Row: {
          id: string
          user_id: string
          word: string
          chinese_meaning: string
          english_meaning: string | null
          phonetic: string | null
          example_sentence: string | null
          synonyms: string[] | null
          antonyms: string[] | null
          difficulty_level: number
          review_count: number
          last_reviewed: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          word: string
          chinese_meaning: string
          english_meaning?: string | null
          phonetic?: string | null
          example_sentence?: string | null
          synonyms?: string[] | null
          antonyms?: string[] | null
          difficulty_level?: number
          review_count?: number
          last_reviewed?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          word?: string
          chinese_meaning?: string
          english_meaning?: string | null
          phonetic?: string | null
          example_sentence?: string | null
          synonyms?: string[] | null
          antonyms?: string[] | null
          difficulty_level?: number
          review_count?: number
          last_reviewed?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      review_sessions: {
        Row: {
          id: string
          user_id: string
          words_reviewed: number
          difficult_words: string[] | null
          session_time: number
          session_type: string
          created_at: string
        }
        Insert: {
          id?: string
          user_id: string
          words_reviewed: number
          difficult_words?: string[] | null
          session_time: number
          session_type: string
          created_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          words_reviewed?: number
          difficult_words?: string[] | null
          session_time?: number
          session_type?: string
          created_at?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
  }
}

export type Word = Database['public']['Tables']['words']['Row']
export type WordInsert = Database['public']['Tables']['words']['Insert']
export type WordUpdate = Database['public']['Tables']['words']['Update']

export type ReviewSession = Database['public']['Tables']['review_sessions']['Row']
export type ReviewSessionInsert = Database['public']['Tables']['review_sessions']['Insert']

export type User = Database['public']['Tables']['users']['Row']