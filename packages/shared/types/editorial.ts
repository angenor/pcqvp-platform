import type { EditorJSData } from './geography'

// --- Hero Section ---

export interface HeroContent {
  title: string
  subtitle: string
  description: string
  image: string | null
}

export interface HeroFieldAdmin {
  value: string
  updated_at: string | null
}

export interface HeroContentAdmin {
  title: HeroFieldAdmin
  subtitle: HeroFieldAdmin
  description: HeroFieldAdmin
  image: HeroFieldAdmin
}

export interface HeroUpdate {
  title: string
  subtitle?: string
  description?: string
  image?: string | null
}

// --- Body ---

export interface BodyContent {
  content_json: EditorJSData | null
}

export interface BodyContentAdmin {
  content_json: EditorJSData | null
  updated_at: string | null
}

export interface BodyUpdate {
  content_json: EditorJSData
}

// --- Footer About ---

export interface FooterAboutContent {
  content_json: EditorJSData | null
}

export interface FooterAboutContentAdmin {
  content_json: EditorJSData | null
  updated_at: string | null
}

export interface FooterAboutUpdate {
  content_json: EditorJSData
}

// --- Contact ---

export interface ContactInfo {
  email: string | null
  phone: string | null
  address: string | null
}

export interface ContactInfoAdmin {
  id: string | null
  email: string | null
  phone: string | null
  address: string | null
  updated_at: string | null
}

export interface ContactInfoUpdate {
  email?: string | null
  phone?: string | null
  address?: string | null
}

// --- Resource Links ---

export interface ResourceLink {
  id: string
  title: string
  url: string
  sort_order: number
}

export interface ResourceLinkAdmin {
  id: string
  title: string
  url: string
  sort_order: number
  updated_at: string | null
}

export interface ResourceLinkCreate {
  title: string
  url: string
  sort_order: number
}

export interface ResourceLinkUpdate {
  title?: string
  url?: string
  sort_order?: number
}

export interface ResourceReorder {
  order: string[]
}

// --- Footer Composite ---

export interface FooterContent {
  about: FooterAboutContent
  contact: ContactInfo
  resources: ResourceLink[]
}

export interface FooterContentAdmin {
  about: FooterAboutContentAdmin
  contact: ContactInfoAdmin
  resources: ResourceLinkAdmin[]
}

// --- Full Editorial Response ---

export interface EditorialPublicResponse {
  hero: HeroContent
  body: BodyContent
  footer: FooterContent
}

export interface EditorialAdminResponse {
  hero: HeroContentAdmin
  body: BodyContentAdmin
  footer: FooterContentAdmin
}
