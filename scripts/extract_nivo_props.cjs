/**
 * Extract the public props of every nivo chart component from the
 * TypeScript declarations shipped on npm.
 *
 * Usage (from an empty scratch directory):
 *   npm i typescript@5 @types/react@19 react@19 react-dom@19 @nivo/<pkg>@<version> ...
 *   node /path/to/extract_nivo_props.cjs bar line pie ... > nivo_props.json
 *
 * The output maps "<package>:<ExportName>" to a list of "propName?: TsType"
 * strings. `generate_components.py` turns that into Reflex components.
 * Packages whose typings are hand-written or missing (geo,
 * parallel-coordinates) are described in `nivo_manual_props.json` instead.
 */
const fs = require("fs");
const ts = require("typescript");

const pkgs = process.argv.slice(2);
const source = pkgs.map((p, i) => `import * as m${i} from '@nivo/${p}';`).join("\n");
fs.writeFileSync("probe.ts", source);

const program = ts.createProgram(["probe.ts"], {
  moduleResolution: ts.ModuleResolutionKind.Bundler,
  module: ts.ModuleKind.ESNext,
  target: ts.ScriptTarget.ES2020,
  jsx: ts.JsxEmit.ReactJSX,
  strict: true,
  skipLibCheck: true,
});
const checker = program.getTypeChecker();
const sourceFile = program.getSourceFile("probe.ts");
const out = {};

sourceFile.statements.forEach((statement, i) => {
  const nsSymbol = checker.getSymbolAtLocation(statement.importClause.namedBindings.name);
  const moduleSymbol = checker.getAliasedSymbol(nsSymbol);
  for (const exp of checker.getExportsOfModule(moduleSymbol)) {
    if (!/^Responsive[A-Z]/.test(exp.name)) continue;
    const type = checker.getTypeOfSymbolAtLocation(exp, statement);
    const signatures = type.getCallSignatures();
    if (!signatures.length) continue;
    const param = signatures[0].getParameters()[0];
    if (!param) continue;
    const propsType = checker.getTypeOfSymbolAtLocation(param, statement);
    const props = checker.getPropertiesOfType(propsType);
    if (!props.length) continue;
    out[`${pkgs[i]}:${exp.name}`] = props.map((prop) => {
      const propType = checker.getTypeOfSymbolAtLocation(prop, statement);
      const optional = prop.flags & ts.SymbolFlags.Optional ? "?" : "";
      const text = checker.typeToString(propType, undefined, ts.TypeFormatFlags.NoTruncation);
      return `${prop.name}${optional}: ${text.slice(0, 200)}`;
    });
  }
});

fs.unlinkSync("probe.ts");
process.stdout.write(JSON.stringify(out, null, 1) + "\n");
