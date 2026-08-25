import { SITE } from "@/content/site";
import {
  StaticPageLayout,
  StaticSection,
} from "@/components/StaticPageLayout";

export function TermsPage() {
  return (
    <StaticPageLayout
      title="Terms of Service"
      subtitle="Terms for using this demo application"
      showLastUpdated
    >
      <StaticSection title="Acceptance">
        <p>
          By accessing or using {SITE.name}, you agree to these Terms of
          Service. If you do not agree, do not use the application.
        </p>
      </StaticSection>

      <StaticSection title="Demo and educational use">
        <p>
          This application is provided as a demonstration and evaluation tool.
          It is not a commercial product, employment portal, or authoritative
          source of company policy.
        </p>
        <p>
          <strong className="text-hf-text">
            HelixForge is a completely fictional company.
          </strong>{" "}
          All corpus content is synthetic. Nothing in this application should
          be relied upon for real-world business, legal, financial, medical, or
          HR decisions.
        </p>
      </StaticSection>

      <StaticSection title="No professional advice">
        <p>
          AI-generated answers may be incomplete, outdated within the demo
          corpus, or incorrect. Responses do not constitute legal, professional,
          or official advice. Always verify information independently before
          acting on it.
        </p>
      </StaticSection>

      <StaticSection title="Acceptable use">
        <p>You agree not to:</p>
        <ul className="list-disc space-y-1 pl-5">
          <li>
            Abuse, overload, or attempt to disrupt the API or underlying
            infrastructure
          </li>
          <li>
            Use the service to process unlawful content or to harass others
          </li>
          <li>
            Misrepresent AI-generated or fictional content as factual or
            official
          </li>
          <li>
            Attempt unauthorized access to systems, data, or accounts
          </li>
        </ul>
      </StaticSection>

      <StaticSection title="Disclaimer of warranties">
        <p>
          The application is provided &ldquo;as is&rdquo; and &ldquo;as
          available,&rdquo; without warranties of any kind, express or implied,
          including accuracy, fitness for a particular purpose, or
          non-infringement.
        </p>
      </StaticSection>

      <StaticSection title="Limitation of liability">
        <p>
          To the fullest extent permitted by law, {SITE.operatorName} shall not
          be liable for any indirect, incidental, special, consequential, or
          punitive damages arising from your use of this demo application.
        </p>
      </StaticSection>

      <StaticSection title="Changes">
        <p>
          These terms may be updated from time to time. Continued use after
          changes are posted constitutes acceptance of the revised terms.
        </p>
      </StaticSection>

      <StaticSection title="Contact">
        <p>
          Operator: {SITE.operatorName}
          <br />
          Email:{" "}
          <a
            href={`mailto:${SITE.operatorEmail}`}
            className="text-hf-teal underline-offset-2 hover:underline"
          >
            {SITE.operatorEmail}
          </a>
        </p>
      </StaticSection>
    </StaticPageLayout>
  );
}
