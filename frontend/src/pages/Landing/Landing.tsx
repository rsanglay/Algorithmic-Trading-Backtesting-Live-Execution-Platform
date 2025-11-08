import React from 'react';
import { Link } from 'react-router-dom';

const Landing: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="max-w-6xl mx-auto px-6 py-8 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
            <span className="text-lg font-bold">AT</span>
          </div>
          <span className="text-xl font-semibold tracking-tight">Algorithmic Trading Platform</span>
        </div>
        <nav className="hidden md:flex items-center space-x-6 text-sm text-slate-200">
          <a href="#solutions" className="hover:text-white transition">Solutions</a>
          <a href="#analytics" className="hover:text-white transition">Analytics</a>
          <a href="#risk" className="hover:text-white transition">Risk & Governance</a>
          <a href="#cta" className="hover:text-white transition">Get Started</a>
        </nav>
        <div className="flex items-center space-x-3">
          <Link to="/login" className="px-4 py-2 text-sm font-medium text-white/70 hover:text-white">Sign in</Link>
          <Link
            to="/register"
            className="px-4 py-2 text-sm font-semibold bg-blue-500 hover:bg-blue-400 rounded-lg"
          >
            Request access
          </Link>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6">
        <section className="py-20 md:py-28">
          <div className="grid md:grid-cols-2 gap-14 items-center">
            <div>
              <span className="inline-flex items-center px-3 py-1 rounded-full bg-blue-500/10 text-xs font-semibold uppercase tracking-widest text-blue-300">
                Quant infrastructure for professional teams
              </span>
              <h1 className="mt-6 text-4xl md:text-5xl font-bold leading-tight">
                Build, validate, and scale systematic strategies with a single institutional-grade platform.
              </h1>
              <p className="mt-6 text-lg text-slate-200 leading-relaxed">
                Design multi-asset portfolios, stress-test execution, and share polished analytics with clients. The platform combines advanced research tooling, automated reporting, and governance-ready controls so your team can focus on alpha.
              </p>
              <div className="mt-8 flex flex-wrap gap-4">
                <Link
                  to="/register"
                  className="px-6 py-3 bg-blue-500 hover:bg-blue-400 rounded-lg font-semibold"
                >
                  Launch workspace
                </Link>
                <a
                  href="#solutions"
                  className="px-6 py-3 border border-white/30 hover:border-white rounded-lg font-semibold text-white/80 hover:text-white"
                >
                  Explore capabilities
                </a>
              </div>
              <div className="mt-12 grid grid-cols-2 gap-6 text-sm text-slate-300">
                <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                  <p className="text-xs uppercase tracking-wide text-slate-400">Trusted by</p>
                  <p className="mt-2 text-lg font-semibold text-white">Research desks, family offices, independent asset managers.</p>
                </div>
                <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                  <p className="text-xs uppercase tracking-wide text-slate-400">Time to insight</p>
                  <p className="mt-2 text-lg font-semibold text-white">Deploy full backtesting & reporting workflows in days, not months.</p>
                </div>
              </div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl p-8 shadow-[0_40px_120px_rgba(15,15,66,0.45)] backdrop-blur">
              <div className="text-sm uppercase text-blue-300">Executive summary</div>
              <h3 className="mt-4 text-xl font-semibold">
                Strategy research, risk analytics, portfolio operations — orchestrated from one control centre.
              </h3>
              <ul className="mt-8 space-y-5 text-sm text-slate-200">
                <li className="flex space-x-3">
                  <span className="mt-1 h-2 w-2 rounded-full bg-blue-400" />
                  <div>
                    <p className="font-semibold text-white">Institutional backtesting & scenario labs</p>
                    <p className="text-slate-300">Walk-forward optimisation, Monte Carlo simulations, execution ready trade logs, and factor-aware attribution.</p>
                  </div>
                </li>
                <li className="flex space-x-3">
                  <span className="mt-1 h-2 w-2 rounded-full bg-blue-400" />
                  <div>
                    <p className="font-semibold text-white">Real-time risk intelligence</p>
                    <p className="text-slate-300">Intraday VaR, stress testing templates, concentration dashboards, and governance-friendly audit trails.</p>
                  </div>
                </li>
                <li className="flex space-x-3">
                  <span className="mt-1 h-2 w-2 rounded-full bg-blue-400" />
                  <div>
                    <p className="font-semibold text-white">Client-ready presentations in minutes</p>
                    <p className="text-slate-300">Automated performance reports, highlight reels, and bespoke investor dashboards tailored to each mandate.</p>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </section>

        <section id="solutions" className="py-16 border-t border-white/10">
          <h2 className="text-3xl font-bold">Solutions crafted for modern quantitative teams</h2>
          <div className="mt-10 grid md:grid-cols-3 gap-8 text-sm text-slate-200">
            <div className="bg-white/5 border border-white/10 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white">Multi-strategy portfolio studio</h3>
              <p className="mt-3">Model long-short equities, macro, and digital assets with reusable templates, regime detection, and allocation overlays.</p>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white">Execution-aware research</h3>
              <p className="mt-3">Simulate order books, slippage, and transaction costs. Validate latency-sensitive ideas before reaching the desk.</p>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white">Stakeholder transparency</h3>
              <p className="mt-3">Role-based dashboards align PMs, risk, and compliance teams with unified analytics and scheduled reporting cadences.</p>
            </div>
          </div>
        </section>

        <section id="analytics" className="py-16 border-t border-white/10">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold">Analytics that answer the hard questions</h2>
              <div className="mt-6 space-y-5 text-slate-200 text-sm leading-relaxed">
                <p>• What portion of returns is true alpha? Break down performance by factor exposures, regimes, and contribution trees.</p>
                <p>• Are we resilient to shocks? Benchmark portfolios against crises, liquidity squeezes, and custom macro narratives.</p>
                <p>• Can we communicate confidence? Package intuitive charts, forward expectations, and risk commentary in investor-ready formats.</p>
              </div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-xl p-6 text-sm text-slate-200">
              <h3 className="text-lg font-semibold text-white">Deliverables out of the box</h3>
              <ul className="mt-4 space-y-3 list-disc list-inside text-slate-300">
                <li>Daily performance and exposure heatmaps.</li>
                <li>Scenario builder for cross-asset stress tests.</li>
                <li>Interactive investor portal with tailored widgets per client.</li>
                <li>Compliance view: position concentration, breach alerts, audit logs.</li>
              </ul>
            </div>
          </div>
        </section>

        <section id="risk" className="py-16 border-t border-white/10">
          <div className="bg-white/5 border border-white/10 rounded-2xl p-8 md:p-10">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="text-3xl font-bold">Risk oversight designed for accountability</h2>
                <p className="mt-4 text-slate-200">
                  Track intraday limits, automate sign-offs, and surface early warnings with narrative-ready summaries. Every action is logged, time-stamped, and ready for auditors.
                </p>
              </div>
              <div className="grid sm:grid-cols-2 gap-6 text-sm text-slate-200">
                <div className="bg-slate-900/60 border border-white/5 rounded-xl p-4">
                  <p className="text-xs uppercase tracking-wide text-slate-400">Instant alignment</p>
                  <p className="mt-2">Role-aware dashboards for CIO, PM, Risk, and Investor Relations teams.</p>
                </div>
                <div className="bg-slate-900/60 border border-white/5 rounded-xl p-4">
                  <p className="text-xs uppercase tracking-wide text-slate-400">Audit proof</p>
                  <p className="mt-2">Immutable activity trail with comments, files, and approvals.</p>
                </div>
                <div className="bg-slate-900/60 border border-white/5 rounded-xl p-4">
                  <p className="text-xs uppercase tracking-wide text-slate-400">Investor clarity</p>
                  <p className="mt-2">Share curated views with LPs without exposing sensitive IP.</p>
                </div>
                <div className="bg-slate-900/60 border border-white/5 rounded-xl p-4">
                  <p className="text-xs uppercase tracking-wide text-slate-400">Fast onboarding</p>
                  <p className="mt-2">Spin up new mandates and configure reporting cadences in minutes.</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="cta" className="py-20 text-center border-t border-white/10">
          <h2 className="text-3xl font-bold">Ready to demonstrate institutional excellence?</h2>
          <p className="mt-4 text-lg text-slate-200">
            Show stakeholders a polished narrative: from research notebooks to production dashboards, risk controls, and investor-ready reporting.
          </p>
          <div className="mt-8 flex justify-center gap-4">
            <Link
              to="/register"
              className="px-8 py-3 bg-blue-500 hover:bg-blue-400 rounded-lg font-semibold"
            >
              Activate sandbox
            </Link>
            <Link
              to="/login"
              className="px-8 py-3 border border-white/30 hover:border-white rounded-lg font-semibold text-white/80 hover:text-white"
            >
              Enter dashboard
            </Link>
          </div>
        </section>
      </main>

      <footer className="border-t border-white/10 py-6 text-center text-sm text-white/60">
        © {new Date().getFullYear()} Algorithmic Trading Platform. Crafted for professional quantitative teams.
      </footer>
    </div>
  );
};

export default Landing;
