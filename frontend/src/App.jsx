import React, { useMemo, useState } from 'react';

const placeholderCatalog = {
  PRODUCT: ['headline', 'price', 'cta', 'image_main'],
  BLOG: ['headline', 'slide_title', 'slide_body', 'image_main'],
  CAMPAIGN: ['headline', 'cta'],
  PARTNER: ['headline', 'partner_logo'],
  EVENT: ['headline', 'date', 'cta']
};

const activeTemplates = [
  { size: 'IG_4x5', template_type: 'PRODUCT' },
  { size: 'LINKEDIN_1x1', template_type: 'PRODUCT' }
];

export function App() {
  const [jobName, setJobName] = useState('Spring Launch Job');
  const [inputMode, setInputMode] = useState('csv');
  const [formValues, setFormValues] = useState({});

  const fields = useMemo(() => {
    const set = new Set();
    activeTemplates.forEach((template) => {
      (placeholderCatalog[template.template_type] || []).forEach((field) => set.add(field));
    });
    return [...set];
  }, []);

  return (
    <main style={{ fontFamily: 'Inter, sans-serif', maxWidth: 980, margin: '40px auto', lineHeight: 1.45 }}>
      <h1>Marketing OS MVP</h1>
      <p>Template registry + bulk content → Figma render → exported assets</p>

      <section style={{ border: '1px solid #ddd', padding: 16, marginBottom: 16 }}>
        <h2>Step 1: Create Bulk Job</h2>
        <label>Job Name
          <input style={{ display: 'block', width: '100%', marginTop: 6 }} value={jobName} onChange={(e) => setJobName(e.target.value)} />
        </label>
        <label style={{ display: 'block', marginTop: 12 }}>Input Source
          <select style={{ display: 'block', marginTop: 6 }} value={inputMode} onChange={(e) => setInputMode(e.target.value)}>
            <option value="csv">Upload CSV</option>
            <option value="json">Paste JSON</option>
            <option value="rss">Connect RSS</option>
          </select>
        </label>
      </section>

      <section style={{ border: '1px solid #ddd', padding: 16, marginBottom: 16 }}>
        <h2>Step 2: Dynamic Placeholder Form</h2>
        {fields.map((field) => (
          <label key={field} style={{ display: 'block', marginBottom: 8 }}>
            {field}
            <input
              style={{ display: 'block', width: '100%', marginTop: 4 }}
              value={formValues[field] || ''}
              onChange={(e) => setFormValues({ ...formValues, [field]: e.target.value })}
              placeholder={field.includes('image') || field.includes('logo') ? 'Image URL' : 'Text value'}
            />
          </label>
        ))}
      </section>

      <section style={{ border: '1px solid #ddd', padding: 16 }}>
        <h2>Step 3-4: Mapping + Generation</h2>
        <p>Map CSV columns to placeholders, review rows, then generate deterministic outputs for every ACTIVE size.</p>
        <button>Generate Job</button>
      </section>
    </main>
  );
}
