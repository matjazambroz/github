<script setup lang="ts">
const { t } = useI18n();

useHead({
  title: t("meta.contact.title"),
  meta: [{ name: "description", content: t("meta.contact.description") }],
});

const form = reactive({ name: "", email: "", company: "", languages: "" });
const submitted = ref(false);

function onSubmit() {
  submitted.value = true;
}

const note = computed(() => {
  if (!submitted.value) return t("contact.form.note");
  const name = form.name.trim();
  return `${t("contact.form.thanksPrefix")}${name ? ", " + name : ""}${t("contact.form.thanksBody")}`;
});
</script>

<template>
  <div>
    <PageHero variant="page" :eyebrow="t('contact.hero.eyebrow')" :title="t('contact.hero.h1')" :lead="t('contact.hero.lead')" />

    <section class="cta">
      <div class="wrap cta-inner">
        <form class="cta-form" @submit.prevent="onSubmit">
          <input v-model="form.name" type="text" name="name" :placeholder="t('contact.form.name')" required autocomplete="name" />
          <input v-model="form.email" type="email" name="email" :placeholder="t('contact.form.email')" required autocomplete="email" />
          <input v-model="form.company" type="text" name="company" :placeholder="t('contact.form.company')" autocomplete="organization" />
          <input v-model="form.languages" type="text" name="languages" :placeholder="t('contact.form.languages')" />
          <button class="btn btn-primary btn-lg" type="submit">{{ t("contact.form.submit") }}</button>
        </form>
        <!-- eslint-disable-next-line vue/no-v-html -->
        <p class="cta-note" v-html="note"></p>
      </div>
    </section>
  </div>
</template>
