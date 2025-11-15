export type FieldComponent =
  | "text"
  | "email"
  | "tel"
  | "date"
  | "textarea"
  | "select"
  | "currency";

export interface FieldDefinition {
  name: string;
  label: string;
  component: FieldComponent;
  required?: boolean;
  placeholder?: string;
  helperText?: string;
  options?: Array<{ label: string; value: string }>;
  defaultValue?: string;
  readOnly?: boolean;
  width?: "full" | "half";
  maxLength?: number;
}

export interface FieldGroupElement {
  type: "field_group";
  title?: string;
  description?: string;
  layout?: "single-column" | "two-column";
  fields: FieldDefinition[];
}

export interface TextElement {
  type: "text";
  style?: "heading" | "subheading" | "body";
  content: string;
}

export interface TableElement {
  type: "table";
  title?: string;
  headers: string[];
  rows: string[][];
}

export interface ListElement {
  type: "list";
  ordered?: boolean;
  items: string[];
}

export interface AcknowledgementListElement {
  type: "acknowledgement_list";
  acknowledgements: Array<{
    id: string;
    label: string;
    required?: boolean;
    maxLength?: number;
  }>;
}

export type SchemaElement =
  | FieldGroupElement
  | TextElement
  | TableElement
  | ListElement
  | AcknowledgementListElement;

export interface AgreementSection {
  id: string;
  title: string;
  description?: string;
  elements: SchemaElement[];
}

export interface AgreementSchema {
  id: string;
  version: string;
  title: string;
  description?: string;
  brand?: {
    schoolName?: string;
    address?: string[];
    phone?: string;
    website?: string;
  };
  sections: AgreementSection[];
}
