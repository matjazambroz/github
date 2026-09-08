export interface MockRow {
  label?: string;
  labelKey?: string;
  value?: string;
  valueKey?: string;
  flag?: boolean;
}

export interface ServiceDef {
  slug: string;
  icon: string;
  prefix: string;
  mock: {
    titleKey: string;
    rows: MockRow[];
    noteKey: string;
    tagKey: string;
  };
  featureKeys: string[];
}

export const services: ServiceDef[] = [
  {
    slug: "translation-localization",
    icon: "🌐",
    prefix: "svcTranslation",
    mock: {
      titleKey: "svcTranslation.mock.title",
      rows: [
        { labelKey: "svcTranslation.mock.sourceLang", value: "EN" },
        { labelKey: "svcTranslation.mock.targetLangs", value: "DE, FR, IT +2" },
        { labelKey: "svcTranslation.mock.contentType", valueKey: "svcTranslation.mock.contentTypeValue" },
        { labelKey: "svcTranslation.mock.status", valueKey: "svcTranslation.mock.statusValue", flag: true },
      ],
      noteKey: "svcTranslation.mock.note",
      tagKey: "svcTranslation.mock.tag",
    },
    featureKeys: ["svcTranslation.f1", "svcTranslation.f2", "svcTranslation.f3", "svcTranslation.f4"],
  },
  {
    slug: "interpretation",
    icon: "🎙️",
    prefix: "svcInterpretation",
    mock: {
      titleKey: "svcInterpretation.mock.title",
      rows: [
        { labelKey: "svcInterpretation.mock.event", valueKey: "svcInterpretation.mock.eventValue" },
        { labelKey: "svcInterpretation.mock.langPair", value: "EN → DE" },
        { labelKey: "svcInterpretation.mock.mode", valueKey: "svcInterpretation.mock.modeValue" },
        { labelKey: "svcInterpretation.mock.status", valueKey: "svcInterpretation.mock.statusValue", flag: true },
      ],
      noteKey: "svcInterpretation.mock.note",
      tagKey: "svcInterpretation.mock.tag",
    },
    featureKeys: ["svcInterpretation.f1", "svcInterpretation.f2", "svcInterpretation.f3", "svcInterpretation.f4"],
  },
  {
    slug: "ai-assisted-translation-qa",
    icon: "🤖",
    prefix: "svcAiQa",
    mock: {
      titleKey: "svcAiQa.mock.title",
      rows: [
        { labelKey: "svcAiQa.mock.langPair", value: "EN → DE" },
        { labelKey: "svcAiQa.mock.aiDraft", valueKey: "svcAiQa.mock.aiDraftValue" },
        { labelKey: "svcAiQa.mock.termCheck", valueKey: "svcAiQa.mock.termCheckValue" },
        { labelKey: "svcAiQa.mock.humanReview", valueKey: "svcAiQa.mock.humanReviewValue", flag: true },
      ],
      noteKey: "svcAiQa.mock.note",
      tagKey: "svcAiQa.mock.tag",
    },
    featureKeys: ["svcAiQa.f1", "svcAiQa.f2", "svcAiQa.f3", "svcAiQa.f4"],
  },
  {
    slug: "terminology-style-management",
    icon: "📖",
    prefix: "svcTerminology",
    mock: {
      titleKey: "svcTerminology.mock.title",
      rows: [
        { label: '"onboarding" → "Einarbeitung"', valueKey: "svcTerminology.mock.approved1" },
        { label: '"dashboard" → "Dashboard"', valueKey: "svcTerminology.mock.approved2" },
        { label: '"customer" → "Kunde"', valueKey: "svcTerminology.mock.underReview", flag: true },
      ],
      noteKey: "svcTerminology.mock.note",
      tagKey: "svcTerminology.mock.tag",
    },
    featureKeys: ["svcTerminology.f1", "svcTerminology.f2", "svcTerminology.f3", "svcTerminology.f4"],
  },
  {
    slug: "multilingual-content-creation",
    icon: "✍️",
    prefix: "svcContent",
    mock: {
      titleKey: "svcContent.mock.title",
      rows: [
        { labelKey: "svcContent.mock.market", valueKey: "svcContent.mock.marketValue" },
        { labelKey: "svcContent.mock.tone", valueKey: "svcContent.mock.toneValue" },
        { labelKey: "svcContent.mock.languages", value: "DE, FR" },
        { labelKey: "svcContent.mock.status", valueKey: "svcContent.mock.statusValue", flag: true },
      ],
      noteKey: "svcContent.mock.note",
      tagKey: "svcContent.mock.tag",
    },
    featureKeys: ["svcContent.f1", "svcContent.f2", "svcContent.f3", "svcContent.f4"],
  },
  {
    slug: "dedicated-language-partner",
    icon: "🤝",
    prefix: "svcPartner",
    mock: {
      titleKey: "svcPartner.mock.title",
      rows: [
        { labelKey: "svcPartner.mock.contact", valueKey: "svcPartner.mock.contactValue" },
        { labelKey: "svcPartner.mock.activeProjects", value: "4" },
        { labelKey: "svcPartner.mock.responseTime", valueKey: "svcPartner.mock.responseTimeValue" },
        { labelKey: "svcPartner.mock.nextCheckin", valueKey: "svcPartner.mock.nextCheckinValue", flag: true },
      ],
      noteKey: "svcPartner.mock.note",
      tagKey: "svcPartner.mock.tag",
    },
    featureKeys: ["svcPartner.f1", "svcPartner.f2", "svcPartner.f3", "svcPartner.f4"],
  },
];
