import { C, F } from '../theme'
import {
  Body,
  Kicker,
  Label,
  Num,
  Panel,
  PanelHead,
  Quote,
  TierBadge,
} from '../ui'
import { TIER_STYLE } from '../theme'
import type { Cited } from '../types'

export default function Method({ d, bundle }: { d: any; bundle: any }) {
  const g = bundle.guardRails
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
      <p
        style={{
          margin: 0,
          maxWidth: '820px',
          font: '300 15px/1.65 ' + F.sans,
          color: C.text3,
        }}
      >
        {d.lede}
      </p>

      <Panel accent={C.heat}>
        <PanelHead
          kicker="GUARD RAIL ONE"
          title={'The method claim is "' + g.methodClaim.headline + '"'}
        />
        <div style={{ padding: '18px 20px', display: 'flex', flexDirection: 'column', gap: '13px' }}>
          <div
            style={{
              padding: '12px 14px',
              border: '1px solid ' + C.heat,
              background: '#1a0e0b',
              font: '500 13px/1.5 ' + F.sans,
              color: '#e8b0a0',
            }}
          >
            {'It is never "' + g.methodClaim.neverClaims + '".'}
          </div>
          <Body>{g.methodClaim.why}</Body>
          {g.methodClaim.evidence.map((e: Cited, i: number) =>
            e.kind === 'quote' ? (
              <Quote key={i} c={e} />
            ) : (
              <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                <Label>FROM THE RECORD</Label>
                <Num c={e} size={12} />
              </div>
            ),
          )}
        </div>
      </Panel>

      <Panel accent={C.recordLine}>
        <PanelHead kicker="GUARD RAIL TWO" title={g.noPromotion.headline} />
        <div style={{ padding: '18px 20px', display: 'flex', flexDirection: 'column', gap: '13px' }}>
          <Quote c={g.noPromotion.rule} />
          <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '7px' }}>
              <Label>THE ONLY LABELS PERMITTED IN A BADGE POSITION</Label>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {g.noPromotion.allowed.map((a: string) => (
                  <span
                    key={a}
                    style={{
                      font: '500 10px/1 ' + F.mono,
                      letterSpacing: '.14em',
                      color: C.text2,
                      border: '1px solid ' + C.lineHard,
                      padding: '5px 9px',
                    }}
                  >
                    {a}
                  </span>
                ))}
              </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '7px' }}>
              <Label>A BUILD FAILURE IF THEY APPEAR ALONE</Label>
              <div style={{ display: 'flex', gap: '8px' }}>
                {g.noPromotion.forbidden.map((a: string) => (
                  <span
                    key={a}
                    style={{
                      font: '500 10px/1 ' + F.mono,
                      letterSpacing: '.14em',
                      color: C.heat,
                      border: '1px solid ' + C.heat,
                      padding: '5px 9px',
                      textDecoration: 'line-through',
                    }}
                  >
                    {a}
                  </span>
                ))}
              </div>
            </div>
          </div>
          <Body style={{ fontSize: '12.5px', color: C.faint }}>
            {g.noPromotion.forbiddenWhy}
          </Body>
        </div>
      </Panel>

      <Panel>
        <PanelHead
          kicker="THE THREE TIERS, ALWAYS VISIBLE"
          title="Every value of record belongs to exactly one, and the verifier proves it"
        />
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit,minmax(260px,1fr))',
          }}
        >
          {d.tiers.map((t: any) => (
            <div
              key={t.tag}
              style={{
                padding: '18px 20px',
                borderRight: '1px solid ' + C.line,
                display: 'flex',
                flexDirection: 'column',
                gap: '10px',
              }}
            >
              <TierBadge tier={t.tag} />
              <span
                style={{
                  font: '500 14px/1.3 ' + F.sans,
                  color: (TIER_STYLE[t.tag] ?? TIER_STYLE.RECORD).col,
                }}
              >
                {t.name}
              </span>
              <Body style={{ fontSize: '12.5px' }}>{t.desc}</Body>
            </div>
          ))}
        </div>
      </Panel>

      <Panel>
        <PanelHead
          kicker="WHAT THE PROGRAM FOUND"
          title="The eight publishable claims, each with the status it holds at the freeze"
        />
        <div style={{ padding: '18px 20px' }}>
          {d.claims.map((c: any) => (
            <div
              key={c.n}
              style={{
                display: 'grid',
                gridTemplateColumns: '34px 1fr 220px',
                gap: '14px',
                padding: '12px 0',
                borderBottom: '1px solid ' + C.lineSoft,
                alignItems: 'start',
              }}
            >
              <span style={{ font: '400 11px/1.5 ' + F.mono, color: C.ghost }}>
                {String(c.n).padStart(2, '0')}
              </span>
              <span style={{ font: '300 13px/1.6 ' + F.sans, color: C.text2 }}>
                {c.text}
              </span>
              <span style={{ font: '400 11px/1.6 ' + F.mono, color: C.muted }}>
                {c.statusText}
              </span>
            </div>
          ))}
          <div style={{ marginTop: '14px' }}>
            <Quote c={d.claimsSource} />
          </div>
        </div>
      </Panel>

      <Panel accent={C.mechanicalLine}>
        <PanelHead
          kicker="WHAT THIS EXHIBIT CANNOT SHOW YOU"
          title="Limitations, stated where you can see them"
        />
        <div style={{ padding: '18px 20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {d.limitations.map((l: any) => (
            <div
              key={l.id}
              style={{ display: 'grid', gridTemplateColumns: '110px 1fr', gap: '14px' }}
            >
              <span style={{ font: '500 11px/1.6 ' + F.mono, color: C.mechanical }}>
                {l.id}
              </span>
              <Body style={{ fontSize: '12.5px' }}>{l.text}</Body>
            </div>
          ))}
        </div>
      </Panel>

      <Panel>
        <PanelHead
          kicker="THE SOURCE INDEX"
          title="Every file this exhibit reads, with its identity"
          right={<TierBadge tier="RECORD" />}
        />
        <div style={{ padding: '16px 20px' }}>
          <div style={{ display: 'flex', gap: '20px', marginBottom: '14px', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
              <Label>PUBLISHED TRACE PAYLOAD</Label>
              <span style={{ font: '400 16px/1 ' + F.mono, color: C.text }}>
                {(d.publishedBytes / 1e6).toFixed(2) + ' MB'}
              </span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
              <Label>TRACES SERVED</Label>
              <span style={{ font: '400 16px/1 ' + F.mono, color: C.text }}>
                {d.traceRows}
              </span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
              <Label>FILES CITED</Label>
              <span style={{ font: '400 16px/1 ' + F.mono, color: C.text }}>
                {d.sources.length}
              </span>
            </div>
          </div>
          {d.sources.map((s: Cited) => (
            <div
              key={s.file}
              style={{
                display: 'grid',
                gridTemplateColumns: 'minmax(240px,1.6fr) 110px 1fr',
                gap: '12px',
                padding: '8px 0',
                borderBottom: '1px solid ' + C.lineSoft,
                alignItems: 'center',
              }}
            >
              <span
                style={{
                  font: '400 11px/1.4 ' + F.mono,
                  color: C.text3,
                  wordBreak: 'break-all',
                }}
              >
                {s.file}
              </span>
              <span style={{ font: '400 11px/1.4 ' + F.mono, color: C.faint }}>
                {((s.bytes ?? 0) / 1024).toFixed(0) + ' KiB'}
              </span>
              <Num c={s} size={10} />
            </div>
          ))}
        </div>
      </Panel>

      <Panel>
        <PanelHead
          kicker="THE VERIFIER"
          title="What has to pass before this page is allowed to exist"
        />
        <div style={{ padding: '18px 20px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <Kicker>exhibit_verify.py</Kicker>
          {[
            'the manifest is exactly the set of values of record in the bundle, re-walked independently',
            'every cited number re-resolves and re-formats to the displayed string, verbatim',
            'every quotation is lifted from its file again and matches character for character',
            'every file fact re-hashes to its stated sha256 and size, and every source-line constant re-parses from its own line',
            'the load-bearing derived numbers are recomputed from the record, and every other derived number names what it came from and claims no key path',
            'no promoted status appears in any badge position, no badge position escapes the enumeration, and no bare status word sits in a section label',
            "the app's own source and its built bundle contain no numeral of record",
            'one decimation row per published trace, with source path, sha256, stride and row count',
            'every 1 Hz file is a strict subsequence of its 10 Hz source and of the published segments',
            'the decimation badge is present verbatim in the data and rendered verbatim on screen',
            "the sandbox model reproduces the record's own force ledgers and ratio ceiling",
            'every adjudication severity count re-parses from its own findings file',
            "every headline number in this workstream's report resolves to the results data and appears in it verbatim",
          ].map((t, i) => (
            <div
              key={i}
              style={{ display: 'grid', gridTemplateColumns: '30px 1fr', gap: '12px' }}
            >
              <span style={{ font: '400 10px/1.6 ' + F.mono, color: C.ghost }}>
                {String(i + 1).padStart(2, '0')}
              </span>
              <span style={{ font: '300 12.5px/1.6 ' + F.sans, color: C.text3 }}>
                {t}
              </span>
            </div>
          ))}
          <Body style={{ fontSize: '12px', color: C.faint }}>
            {'The badge discipline and the verifier are not polish. An exhibit that displayed one unverifiable number would refute the thing it exists to demonstrate.'}
          </Body>
        </div>
      </Panel>
    </div>
  )
}
