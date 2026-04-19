import { Callout } from '../components/ui/Callout'
import { CodeBlock } from '../components/ui/CodeBlock'
import { CommandCard } from '../components/ui/CommandCard'
import { Hero } from '../components/ui/Hero'
import { Section } from '../components/ui/Section'
import { Sidebar } from '../components/ui/Sidebar'
import { StepCard } from '../components/ui/StepCard'
import { Tabs } from '../components/ui/Tabs'
import { Topbar } from '../components/ui/Topbar'

const DOCS_VERSION = '1.2.5'
const TYPESCRIPT_DOCS_VERSION = '1.2.5'

const sidebarItems = [
  { id: 'problem-solution', label: 'Problem & Solution' },
  { id: 'installation', label: 'Installation' },
  { id: 'typescript-docs', label: 'TypeScript' },
  { id: 'sql-engines', label: 'Supported SQL Engines' },
  { id: 'quick-start', label: 'Quick Start' },
  { id: 'cache-performance', label: 'Cache & Performance' },
  { id: 'e2e-examples', label: 'E2E Examples' },
  { id: 'api-reference', label: 'API Reference' },
  { id: 'advanced-prompt-utilities', label: 'Advanced Prompt Utilities' },
  { id: 'internals', label: 'How It Works Internally' },
  { id: 'backend-comparison', label: 'Backend Comparison' },
  { id: 'limitations', label: 'Current Limitations' },
  { id: 'tests-license', label: 'Tests & License' },
]

const installTabs = [
  {
    id: 'base-install',
    label: 'Base',
    content: <CommandCard command={'pip install naturalsql'} />,
  },
  {
    id: 'extras-install',
    label: 'Extras',
    content: (
      <CodeBlock
        title="Optional extras"
        language="bash"
        code={[
          'pip install "naturalsql[chroma-local]"',
          'pip install "naturalsql[sqlite-local]"',
          'pip install "naturalsql[sqlite-gemini]"',
          'pip install "naturalsql[chroma-gemini]"',
          'pip install naturalsql[postgresql]',
          'pip install naturalsql[mysql]',
          'pip install naturalsql[sqlserver]',
          'pip install naturalsql[all-db]',
        ].join('\n')}
      />
    ),
  },
]

const quickStartCode = [
  'from naturalsql import NaturalSQL',
  '',
  'nsql = NaturalSQL(',
  '    db_url="postgresql://user:password@localhost:5432/mydb",',
  '    db_type="postgresql",',
  ')',
  '',
  'result = nsql.build_vector_db(storage_path="./metadata_vdb", forced_reset=False)',
  'print(f"Indexed documents: {result[\'indexed_documents\']}")',
  'print(f"From cache: {result[\'from_cache\']}")',
  '',
  'tables = nsql.search("Show me sales from last month", limit=3)',
  'for table in tables:',
  '    print(table)',
].join('\n')

const constructorReference = [
  'from naturalsql import NaturalSQL',
  '',
  'nsql = NaturalSQL(',
  '    db_url="postgresql://user:password@localhost:5432/mydb",',
  '    db_type="postgresql",',
  '    db_normalize_embeddings=True,',
  '    device="cpu",',
  '    vector_backend="chroma",',
  '    embedding_provider="local",',
  '    gemini_api_key=None,',
  '    gemini_embedding_model="gemini-embedding-2-preview",',
  '    vector_distance_threshold=1.0,',
  ')',
].join('\n')

const e2eTabs = [
  {
    id: 'chroma-local',
    label: 'chroma-local',
    content: (
      <CodeBlock
        title="e2e_chroma_local.py"
        language="python"
        code={[
          'from naturalsql import NaturalSQL',
          '',
          'nsql = NaturalSQL(',
          '    db_url="postgresql://user:pass@localhost:5432/mydb",',
          '    db_type="postgresql",',
          '    vector_backend="chroma",',
          '    embedding_provider="local",',
          '    vector_distance_threshold=1.6,  # if search() returns [], try 1.4-1.6',
          ')',
          '',
          'nsql.build_vector_db(storage_path="./metadata_vdb", forced_reset=False)',
          'tables = nsql.search("sales for the last month", limit=3)',
          'print(tables)',
        ].join('\n')}
      />
    ),
  },
  {
    id: 'sqlite-gemini',
    label: 'sqlite-gemini',
    content: (
      <CodeBlock
        title="e2e_sqlite_gemini.py"
        language="python"
        code={[
          'import os',
          'from naturalsql import NaturalSQL',
          '',
          'nsql = NaturalSQL(',
          '    db_url="sqlite:///./app.db",',
          '    db_type="sqlite",',
          '    vector_backend="sqlite",',
          '    embedding_provider="gemini",',
          '    gemini_api_key=os.environ["GEMINI_API_KEY"],',
          '    gemini_embedding_model="gemini-embedding-2-preview",',
          ')',
          '',
          'nsql.build_vector_db(storage_path="./metadata_vdb_sqlite", forced_reset=False)',
          'tables = nsql.search("users with recent purchases", limit=3)',
          'print(tables)',
        ].join('\n')}
      />
    ),
  },
]

const tsInstallCode = [
  '# Base package',
  'npm i naturalsql',
  '',
  '# Chroma + local embeddings',
  'npm i chromadb @xenova/transformers',
  '',
  '# SQLite + local embeddings',
  'npm i better-sqlite3 @xenova/transformers',
  '',
  '# SQLite + Gemini embeddings',
  'npm i better-sqlite3 @google/generative-ai',
  '',
  '# Chroma + Gemini embeddings',
  'npm i chromadb @google/generative-ai',
  '',
  '# PostgreSQL driver support',
  'npm i pg',
  '',
  '# MySQL driver support',
  'npm i mysql2',
  '',
  '# SQL Server driver support',
  'npm i mssql',
].join('\n')

const tsQuickStartCode = [
  'import { NaturalSQL } from "naturalsql";',
  '',
  'const nsql = new NaturalSQL({',
  '  dbUrl: "postgresql://user:password@localhost:5432/mydb",',
  '  dbType: "postgresql"',
  '});',
  '',
  'const result = await nsql.buildVectorDb("./metadata_vdb");',
  'console.log(`Indexed tables: ${result.indexedTables}`);',
  'console.log(`From cache: ${result.fromCache}`);',
  '',
  'const tables = await nsql.search("Show me sales from last month", {',
  '  storagePath: "./metadata_vdb",',
  '  limit: 3',
  '});',
  '',
  'for (const table of tables) {',
  '  console.log(table);',
  '}',
].join('\n')

const tsE2EChromaLocalCode = [
  'import { NaturalSQL } from "naturalsql";',
  '',
  'const nsql = new NaturalSQL({',
  '  dbUrl: "postgresql://user:pass@localhost:5432/mydb",',
  '  dbType: "postgresql",',
  '  vectorBackend: "chroma",',
  '  embeddingProvider: "local",',
  '  vectorDistanceThreshold: 0.35',
  '});',
  '',
  'await nsql.buildVectorDb("./metadata_vdb", { forceReset: false });',
  'const tables = await nsql.search("sales for the last month", {',
  '  storagePath: "./metadata_vdb",',
  '  limit: 3',
  '});',
  'console.log(tables);',
].join('\n')

const tsE2ESqliteGeminiCode = [
  'import { NaturalSQL } from "naturalsql";',
  '',
  'const nsql = new NaturalSQL({',
  '  dbUrl: "sqlite:///./app.db",',
  '  dbType: "sqlite",',
  '  vectorBackend: "sqlite",',
  '  embeddingProvider: "gemini",',
  '  geminiApiKey: process.env.GEMINI_API_KEY,',
  '  geminiEmbeddingModel: "text-embedding-004"',
  '});',
  '',
  'await nsql.buildVectorDb("./metadata_vdb_sqlite", { forceReset: false });',
  'const tables = await nsql.search("users with recent purchases", {',
  '  storagePath: "./metadata_vdb_sqlite",',
  '  limit: 3',
  '});',
  'console.log(tables);',
].join('\n')

const tsBuildPromptCode = [
  'import { buildPrompt } from "naturalsql";',
  '',
  'const prompt = buildPrompt(tables, "Show me sales from last month");',
].join('\n')

const tsDevCommandsCode = ['npm run test', 'npm run typecheck', 'npm run build'].join('\n')

export default function Documentation() {
  return (
    <main className="h-full min-h-0 overflow-y-auto bg-linear-to-b from-emerald-50 via-slate-50 to-white text-slate-900">
      <div className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <Topbar
          title="NaturalSQL Documentation"
          subtitle="Library-focused docs for schema extraction, vector indexing, and retrieval for SQL-aware LLM workflows."
        />

        <div className="mt-6 grid gap-6 lg:grid-cols-[250px_minmax(0,1fr)]">
          <Sidebar title="Documentation" items={sidebarItems} />

          <div className="space-y-6">
            <Hero
              badge={`v${DOCS_VERSION}`}
              title="Turn SQL schema into reliable LLM context"
              description="NaturalSQL extracts live SQL schema metadata, builds semantic documents, stores embeddings in Chroma or SQLite, and retrieves the most relevant context for natural-language SQL requests."
            />

            <Section
              id="problem-solution"
              eyebrow="Overview"
              title="Problem and solution"
              description="NaturalSQL is built for teams that need SQL-aware LLM context without adopting a heavyweight framework."
            >
              <Callout title="Problem">
                LLMs often generate incorrect SQL when they lack real schema context (table names, column types, and
                foreign-key relationships).
              </Callout>
              <Callout title="Solution">
                NaturalSQL reads metadata from your live database, generates schema documents, embeds them, and retrieves
                relevant context at query time for prompt grounding.
              </Callout>
            </Section>

            <Section id="installation" eyebrow="Setup" title="Installation">
              <Tabs tabs={installTabs} />
              <Callout title="Notes">
                SQLite support uses Python&apos;s standard library. If you use Gemini embeddings, provide
                <code> GEMINI_API_KEY </code> via environment variables.
              </Callout>
            </Section>

            <Section
              id="typescript-docs"
              eyebrow="TypeScript"
              title="NaturalSQL TypeScript"
              description="Lightweight library to convert your SQL database schema into a vector database, so LLMs can use real table/column context to generate more accurate SQL from natural language."
            >
              <Callout title={`Version v${TYPESCRIPT_DOCS_VERSION}`}>
                Node.js <code>&gt;=18</code> is required. For Gemini, use <code>@google/generative-ai</code> and
                environment variables like <code>GEMINI_API_KEY</code> (never hardcode secrets).
              </Callout>
              <Callout title="Problem">
                Sometimes you want to interact with SQL databases through an LLM without pulling in large frameworks
                with many unrelated features.
              </Callout>
              <Callout title="Solution">
                NaturalSQL extracts your database schema, vectorizes it using a configurable backend
                (<code>chroma</code> or <code>sqlite</code>) and embedding provider (<code>local</code> or
                <code> gemini</code>), then retrieves relevant schema context for your LLM.
              </Callout>

              <StepCard step="01" title="Installation">
                <CodeBlock title="install_typescript.sh" language="bash" code={tsInstallCode} />
              </StepCard>

              <StepCard step="02" title="Quick start">
                <CodeBlock title="quickstart.ts" language="ts" code={tsQuickStartCode} />
              </StepCard>

              <StepCard step="03" title="Automatic cache">
                <p>
                  <code>buildVectorDb()</code> reuses vector storage when possible (same storage path + schema cache
                  key), unless <code>forceReset: true</code> is provided.
                </p>
                <p>
                  Also, <code>search()</code> reuses the in-memory <code>VectorManager</code> for the same
                  <code> storagePath</code> to reduce repeated initialization cost.
                </p>
              </StepCard>

              <StepCard step="04" title="Supported SQL engines">
                <ul className="list-disc space-y-1 pl-6 text-slate-700">
                  <li>PostgreSQL</li>
                  <li>MySQL</li>
                  <li>SQL Server</li>
                  <li>SQLite</li>
                </ul>
              </StepCard>

              <StepCard step="05" title="E2E examples">
                <CodeBlock title="e2e_chroma_local.ts" language="ts" code={tsE2EChromaLocalCode} />
                <div className="mt-3" />
                <CodeBlock title="e2e_sqlite_gemini.ts" language="ts" code={tsE2ESqliteGeminiCode} />
              </StepCard>

              <StepCard step="06" title="API">
                <p className="mb-3">
                  <code>new NaturalSQL(options?)</code> creates an instance with DB and embedding configuration.
                </p>
                <div className="overflow-x-auto rounded-xl border border-slate-200">
                  <table className="min-w-full divide-y divide-slate-200 text-sm">
                    <thead className="bg-slate-50">
                      <tr>
                        <th className="px-4 py-3 text-left font-semibold text-slate-700">Parameter</th>
                        <th className="px-4 py-3 text-left font-semibold text-slate-700">Type</th>
                        <th className="px-4 py-3 text-left font-semibold text-slate-700">Default</th>
                        <th className="px-4 py-3 text-left font-semibold text-slate-700">Description</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200 bg-white">
                      <tr>
                        <td className="px-4 py-3 font-medium text-slate-700">dbUrl</td>
                        <td className="px-4 py-3 text-slate-600">string | null</td>
                        <td className="px-4 py-3 text-slate-600">null</td>
                        <td className="px-4 py-3 text-slate-600">Database connection URL</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-3 font-medium text-slate-700">dbType</td>
                        <td className="px-4 py-3 text-slate-600">string</td>
                        <td className="px-4 py-3 text-slate-600">sqlite</td>
                        <td className="px-4 py-3 text-slate-600">postgresql, mysql, sqlite, sqlserver</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-3 font-medium text-slate-700">normalizeEmbeddings</td>
                        <td className="px-4 py-3 text-slate-600">boolean</td>
                        <td className="px-4 py-3 text-slate-600">true</td>
                        <td className="px-4 py-3 text-slate-600">Normalize embedding vectors</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-3 font-medium text-slate-700">device</td>
                        <td className="px-4 py-3 text-slate-600">string</td>
                        <td className="px-4 py-3 text-slate-600">cpu</td>
                        <td className="px-4 py-3 text-slate-600">Embedding device: cpu or cuda</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-3 font-medium text-slate-700">vectorBackend</td>
                        <td className="px-4 py-3 text-slate-600">chroma | sqlite</td>
                        <td className="px-4 py-3 text-slate-600">sqlite</td>
                        <td className="px-4 py-3 text-slate-600">Vector backend</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-3 font-medium text-slate-700">embeddingProvider</td>
                        <td className="px-4 py-3 text-slate-600">local | gemini</td>
                        <td className="px-4 py-3 text-slate-600">local</td>
                        <td className="px-4 py-3 text-slate-600">Embedding provider</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-3 font-medium text-slate-700">geminiApiKey</td>
                        <td className="px-4 py-3 text-slate-600">string | null</td>
                        <td className="px-4 py-3 text-slate-600">null</td>
                        <td className="px-4 py-3 text-slate-600">Required when embeddingProvider=gemini</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-3 font-medium text-slate-700">geminiEmbeddingModel</td>
                        <td className="px-4 py-3 text-slate-600">string</td>
                        <td className="px-4 py-3 text-slate-600">text-embedding-004</td>
                        <td className="px-4 py-3 text-slate-600">Gemini embedding model</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-3 font-medium text-slate-700">vectorDistanceThreshold</td>
                        <td className="px-4 py-3 text-slate-600">number</td>
                        <td className="px-4 py-3 text-slate-600">0.35</td>
                        <td className="px-4 py-3 text-slate-600">Max distance threshold used by search()</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <p className="mt-4 mb-2 font-medium text-slate-700">Supported backend/provider combinations</p>
                <ul className="list-disc space-y-1 pl-6 text-slate-700">
                  <li>chroma + local</li>
                  <li>sqlite + local</li>
                  <li>sqlite + gemini</li>
                  <li>chroma + gemini</li>
                </ul>

                <div className="mt-4 overflow-x-auto rounded-xl border border-slate-200">
                  <table className="min-w-full divide-y divide-slate-200 text-sm">
                    <thead className="bg-slate-50">
                      <tr>
                        <th className="px-4 py-3 text-left font-semibold text-slate-700">Method</th>
                        <th className="px-4 py-3 text-left font-semibold text-slate-700">Summary</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200 bg-white">
                      <tr>
                        <td className="px-4 py-3 font-medium text-slate-700">
                          await nsql.buildVectorDb(storagePath, options?)
                        </td>
                        <td className="px-4 py-3 text-slate-600">
                          Extracts schema and indexes it. Supports <code>forceReset</code> and optional
                          <code> cacheKey</code>. Returns <code>storagePath</code>, <code>indexedTables</code>, and
                          <code> fromCache</code>.
                        </td>
                      </tr>
                      <tr>
                        <td className="px-4 py-3 font-medium text-slate-700">await nsql.search(request, options?)</td>
                        <td className="px-4 py-3 text-slate-600">
                          Retrieves semantically relevant tables. Options include <code>storagePath</code> (default
                          ./metadata_vdb) and <code>limit</code> (default 3).
                        </td>
                      </tr>
                      <tr>
                        <td className="px-4 py-3 font-medium text-slate-700">
                          buildPrompt(relevantTables, userQuestion)
                        </td>
                        <td className="px-4 py-3 text-slate-600">
                          Helper to create an LLM prompt from retrieved tables and a user question.
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div className="mt-4">
                  <CodeBlock title="build_prompt.ts" language="ts" code={tsBuildPromptCode} />
                </div>
              </StepCard>

              <StepCard step="07" title="Technical strategy">
                <ol className="list-decimal space-y-2 pl-6 text-slate-700">
                  <li>Connection via native drivers (pg, mysql2, mssql) or SQLite support.</li>
                  <li>Schema extraction via engine-specific metadata queries or PRAGMA for SQLite.</li>
                  <li>Vectorization into semantic documents indexed in chroma or sqlite.</li>
                  <li>Retrieval via nearest-neighbor search with vectorDistanceThreshold filtering.</li>
                  <li>Caching through schema-key reuse and in-memory manager reuse.</li>
                </ol>
              </StepCard>

              <StepCard step="08" title="Development">
                <CodeBlock title="dev_commands.sh" language="bash" code={tsDevCommandsCode} />
              </StepCard>
            </Section>

            <Section id="sql-engines" eyebrow="Compatibility" title="Supported SQL engines">
              <div className="grid gap-3 sm:grid-cols-2">
                <StepCard step="01" title="PostgreSQL">
                  <p>Supported through optional PostgreSQL driver extras.</p>
                </StepCard>
                <StepCard step="02" title="MySQL">
                  <p>Supported through optional MySQL driver extras.</p>
                </StepCard>
                <StepCard step="03" title="SQL Server">
                  <p>Supported through optional SQL Server driver extras.</p>
                </StepCard>
                <StepCard step="04" title="SQLite">
                  <p>Supported out of the box for local and embedded workflows.</p>
                </StepCard>
              </div>
            </Section>

            <Section
              id="quick-start"
              eyebrow="Getting Started"
              title="Quick start"
              description="Use this baseline flow to configure, index, and retrieve schema context."
            >
              <StepCard step="01" title="Create the client">
                <p>Initialize NaturalSQL with your SQL connection details and optional vector settings.</p>
              </StepCard>
              <StepCard step="02" title="Build vector storage">
                <p>Extract schema metadata and index documents into your configured backend.</p>
              </StepCard>
              <StepCard step="03" title="Search relevant context">
                <p>Retrieve top semantic matches for a question and pass them into your LLM prompt.</p>
              </StepCard>
              <CodeBlock title="quickstart.py" language="python" code={quickStartCode} />
              <Callout title="indexed_documents meaning">
                <code>indexed_documents</code> is the total number of generated schema documents indexed in the vector
                store. In most schemas this includes table documents plus relationship documents, not only raw table
                count.
              </Callout>
            </Section>

            <Section
              id="cache-performance"
              eyebrow="Runtime"
              title="Cache and performance behavior"
              description="NaturalSQL is optimized for repeated retrieval over stable schemas."
            >
              <Callout title="Model warm-up">
                The first <code>search()</code> call loads embedding resources and is typically slower. Subsequent calls
                reuse the in-memory instance and are usually much faster.
              </Callout>
              <Callout title="Index reuse">
                <code>build_vector_db(forced_reset=False)</code> reuses existing persisted storage when available,
                reducing unnecessary reindexing and startup cost.
              </Callout>
            </Section>

            <Section id="e2e-examples" eyebrow="Examples" title="End-to-end configurations">
              <Tabs tabs={e2eTabs} />
            </Section>

            <Section
              id="api-reference"
              eyebrow="Reference"
              title="API reference"
              description="Core entry points used in most NaturalSQL integrations."
            >
              <StepCard step="01" title="NaturalSQL(...) constructor">
                <p>
                  Required: <code>db_url</code>, <code>db_type</code>. Optional controls include
                  <code> vector_backend</code>, <code>embedding_provider</code>,
                  <code> db_normalize_embeddings</code>, <code>device</code>, and Gemini settings.
                </p>
                <CodeBlock title="constructor.py" language="python" code={constructorReference} />
              </StepCard>
              <StepCard step="02" title="build_vector_db(storage_path, forced_reset) -&gt; dict">
                <p>
                  Connects to the database, extracts schema metadata, generates semantic documents, and indexes them in
                  the selected backend.
                </p>
              </StepCard>
              <StepCard step="03" title="search(request, storage_path, limit) -&gt; list">
                <p>
                  Embeds the question, retrieves nearest schema documents, applies distance thresholding, and returns
                  mixed context documents (usually <code>table</code> and <code>relationship</code> kinds) that you can
                  feed into your own SQL or answer-generation prompt flow.
                </p>
              </StepCard>
              <Callout title="Scope of the core class">
                <code>NaturalSQL</code> focuses on schema indexing and semantic retrieval. End-to-end SQL generation and
                final natural-language narration are not included by default in the core class, but advanced helpers in
                <code> naturalsql.utils.prompt </code> can accelerate that layer in your application.
              </Callout>
            </Section>

            <Section
              id="advanced-prompt-utilities"
              eyebrow="Advanced"
              title="Advanced Prompt Utilities"
              description="Optional helpers for teams that want to move from retrieved context to chat-ready prompts."
            >
              <Callout title="Positioning">
                Utilities in <code>naturalsql.utils.prompt</code> are advanced user helpers, not the core public API
                surface of <code>NaturalSQL</code> itself.
              </Callout>
              <StepCard
                step="01"
                title="build_prompt(relevant_tables, user_question, db_type) -&gt; list[dict[str, str]]"
              >
                <p>
                  Builds a chat-style message list (for example, system + user messages) from retrieved schema context.
                  It does not return a single string, and <code>db_type</code> is required so the prompt can steer SQL
                  dialect behavior.
                </p>
                <CodeBlock
                  title="advanced_build_prompt.py"
                  language="python"
                  code={[
                    'from naturalsql import NaturalSQL',
                    'from naturalsql.utils.prompt import build_prompt',
                    '',
                    'nsql = NaturalSQL(db_url="postgresql://user:pass@localhost:5432/mydb", db_type="postgresql")',
                    'nsql.build_vector_db(storage_path="./metadata_vdb", forced_reset=False)',
                    '',
                    'context_docs = nsql.search("Show monthly revenue by region", limit=4)',
                    'messages = build_prompt(',
                    '    relevant_tables=context_docs,',
                    '    user_question="Show monthly revenue by region",',
                    '    db_type="postgresql",',
                    ')',
                    '',
                    '# messages can be sent directly to a chat-completions API',
                    'print(messages[0])',
                  ].join('\n')}
                />
                <Callout title="Caveat">
                  Pass the same <code>db_type</code> used in your NaturalSQL client; mixing dialects can degrade SQL
                  quality.
                </Callout>
              </StepCard>
              <StepCard step="02" title="prompt_query(question, query_response) -&gt; list[dict[str, str]]">
                <p>
                  Builds a second-stage chat-style prompt to explain SQL query results in plain language after execution.
                  Use it when your pipeline already ran SQL and now needs user-facing narration.
                </p>
                <CodeBlock
                  title="advanced_prompt_query.py"
                  language="python"
                  code={[
                    'from naturalsql.utils.prompt import prompt_query',
                    '',
                    'rows = [',
                    '    {"month": "2026-01", "revenue": 124500.0},',
                    '    {"month": "2026-02", "revenue": 118900.0},',
                    ']',
                    '',
                    'messages = prompt_query(',
                    '    question="How did revenue trend in the last two months?",',
                    '    query_response=rows,',
                    ')',
                    '',
                    'print(messages[-1])',
                  ].join('\n')}
                />
                <Callout title="Caveat">
                  <code>prompt_query</code> does not execute SQL. It expects trusted query output from your own DB
                  execution layer.
                </Callout>
              </StepCard>
            </Section>

            <Section
              id="internals"
              eyebrow="Architecture"
              title="How it works internally"
              description="NaturalSQL follows a deterministic retrieval pipeline across SQL engines."
            >
              <StepCard step="01" title="Schema extraction">
                <p>
                  Connects to your DB and extracts metadata with engine-specific introspection (system views/queries or
                  SQLite PRAGMA). Internal/system tables are excluded during this stage.
                </p>
              </StepCard>
              <StepCard step="02" title="Normalization">
                <p>Converts engine-specific metadata into a unified schema dictionary.</p>
              </StepCard>
              <StepCard step="03" title="formated_for_ia document generation">
                <p>
                  Generates <code>formated_for_ia</code> semantic documents (usually table + relationship docs) from the
                  normalized schema.
                </p>
              </StepCard>
              <StepCard step="04" title="Embeddings">
                <p>Embeds documents with local sentence-transformers or Gemini.</p>
              </StepCard>
              <StepCard step="05" title="Storage">
                <p>Persists vectors and metadata in either a Chroma collection or SQLite <code>vectors.db</code>.</p>
              </StepCard>
              <StepCard step="06" title="Retrieval">
                <p>
                  <code>search()</code> embeds the user query, applies kind-based filtering and distance-threshold
                  filtering, and returns the best context documents for downstream prompting.
                </p>
              </StepCard>
              <Callout title="Storage behavior details">
                Chroma uses a persistent collection with native metadata filtering. SQLite stores rows in
                <code> vectors.db </code> with embedding data and metadata JSON, then computes cosine distance at query
                time to rank nearest documents.
              </Callout>
            </Section>

            <Section id="backend-comparison" eyebrow="Backends" title="Chroma vs SQLite">
              <div className="overflow-x-auto rounded-xl border border-slate-200">
                <table className="min-w-full divide-y divide-slate-200 text-sm">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-4 py-3 text-left font-semibold text-slate-700">Aspect</th>
                      <th className="px-4 py-3 text-left font-semibold text-slate-700">Chroma</th>
                      <th className="px-4 py-3 text-left font-semibold text-slate-700">SQLite</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 bg-white">
                    <tr>
                      <td className="px-4 py-3 font-medium text-slate-700">Storage files</td>
                      <td className="px-4 py-3 text-slate-600">Persistent Chroma directory</td>
                      <td className="px-4 py-3 text-slate-600">Local <code>vectors.db</code> file</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-3 font-medium text-slate-700">Vector query</td>
                      <td className="px-4 py-3 text-slate-600">Native vector query</td>
                      <td className="px-4 py-3 text-slate-600">Cosine distance in Python</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-3 font-medium text-slate-700">Metadata filtering</td>
                      <td className="px-4 py-3 text-slate-600">Native where filtering</td>
                      <td className="px-4 py-3 text-slate-600">JSON metadata filtering</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-3 font-medium text-slate-700">Operational profile</td>
                      <td className="px-4 py-3 text-slate-600">Dedicated vector database style</td>
                      <td className="px-4 py-3 text-slate-600">Lightweight embedded store</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </Section>

            <Section id="limitations" eyebrow="Reality Check" title="Current limitations">
              <Callout title="Ranking strategy">
                Current retrieval is embedding-distance based and does not include hybrid lexical reranking.
              </Callout>
              <Callout title="Relationship semantics">
                Relationship text is intentionally concise, so very complex semantic constraints are not explicitly encoded.
              </Callout>
              <Callout title="SQLite scaling">
                SQLite backend computes similarity in Python, so very large corpora can be slower than native vector
                engines.
              </Callout>
            </Section>

            <Section id="tests-license" eyebrow="Project" title="Tests and license">
              <StepCard step="01" title="Tests">
                <p>
                  See{' '}
                  <a
                    className="font-medium text-emerald-700 underline decoration-emerald-300 underline-offset-2"
                    href="https://github.com/Zay-M3/NaturalSQL/blob/main/test/README.md"
                    target="_blank"
                    rel="noreferrer"
                  >
                    test/README.md
                  </a>{' '}
                  for test setup and execution.
                </p>
              </StepCard>
              <StepCard step="02" title="License">
                <p>
                  NaturalSQL is distributed under the{' '}
                  <a
                    className="font-medium text-emerald-700 underline decoration-emerald-300 underline-offset-2"
                    href="https://github.com/Zay-M3/NaturalSQL/blob/main/LICENSE"
                    target="_blank"
                    rel="noreferrer"
                  >
                    Apache License 2.0
                  </a>
                  .
                </p>
              </StepCard>
            </Section>
          </div>
        </div>
      </div>
    </main>
  )
}
