import { SITE } from "@/content/site";
import {
  StaticPageLayout,
  StaticSection,
} from "@/components/StaticPageLayout";

export function PrivacyPage() {
  return (
    <StaticPageLayout
      title="Privacy Policy"
      subtitle="How this demo handles your data"
      showLastUpdated
    >
      <StaticSection title="Overview">
        <p>
          {SITE.name} is a demo application operated by {SITE.operatorName}.
          This policy describes what information may be processed when you use
          the site.
        </p>
        <p>
          <strong className="text-hf-text">
            HelixForge is a completely fictional company.
          </strong>{" "}
          The policy corpus contains synthetic demo data only — not real
          employee or customer records.
        </p>
      </StaticSection>

      <StaticSection title="Information we collect">
        <p>When you use the application, the following may be processed:</p>
        <ul className="list-disc space-y-1 pl-5">
          <li>
            <strong className="text-hf-text">Questions you submit</strong> —
            sent to the FastAPI backend at <code className="text-xs">/api/ask</code>{" "}
            to generate answers
          </li>
          <li>
            <strong className="text-hf-text">Chat history</strong> — kept in
            browser memory for the current session (not persisted to a user
            account)
          </li>
          <li>
            <strong className="text-hf-text">Theme preference</strong> — stored
            in your browser&apos;s <code className="text-xs">localStorage</code>{" "}
            under <code className="text-xs">hf-theme</code>
          </li>
          <li>
            <strong className="text-hf-text">Evaluation data</strong> — RAG eval
            runs and scores stored server-side in SQLite as part of the demo
            (not linked to user accounts)
          </li>
        </ul>
      </StaticSection>

      <StaticSection title="Information we do not collect">
        <ul className="list-disc space-y-1 pl-5">
          <li>User accounts or passwords</li>
          <li>Payment or billing information</li>
          <li>Real HelixForge employee or customer data (the company is fictional)</li>
        </ul>
        <p>
          Do not submit sensitive personal information. Anything you type into
          the Ask interface may be forwarded to third-party AI services.
        </p>
      </StaticSection>

      <StaticSection title="Third-party services">
        <p>
          When configured, question answering uses third-party LLM providers
          (e.g. Groq) to generate responses. Those providers process the text
          of your questions according to their own privacy policies.
        </p>
        <p>
          Embedding and retrieval run locally or on the server hosting this
          demo; no separate cloud vector DB is required for the default setup.
        </p>
      </StaticSection>

      <StaticSection title="Data retention">
        <p>
          Browser chat history is ephemeral and cleared when you refresh or
          close the tab unless you keep the session open. Theme preferences
          remain in localStorage until you clear site data.
        </p>
        <p>
          Server-side eval logs and SQLite records persist on the host machine
          for demonstration purposes. They are not tied to individual user
          identities.
        </p>
      </StaticSection>

      <StaticSection title="Your choices">
        <p>
          You can clear localStorage and browser data at any time through your
          browser settings. You may stop using the application at any time.
        </p>
      </StaticSection>

      <StaticSection title="Contact">
        <p>
          Privacy questions? Contact {SITE.operatorName} at{" "}
          <a
            href={`mailto:${SITE.operatorEmail}`}
            className="text-hf-teal underline-offset-2 hover:underline"
          >
            {SITE.operatorEmail}
          </a>
          .
        </p>
      </StaticSection>
    </StaticPageLayout>
  );
}
