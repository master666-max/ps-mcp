# 发布前四查（缺一不发）— ps-mcp

实现：`run-regression-checks.py`（stdlib only；根目录=evals/ 的上级）。与达芬奇同族
runner 语义一致（复用惯例，docs/decisions D7）。

## 四查定义

1. **① 指纹回归全量 PASS**：`fingerprint-table.md` 每行的指纹串在其锚文件中存在。
   FAIL → exit 1。
2. **② 版本三处同步**：SKILL.md frontmatter `version:` == INSTALL.md 标题 `v<版本>` ==
   CHANGELOG.md 最新条目 `## <版本>`。FAIL → exit 2。
3. **③ 部署逐根哈希断言**：存在 `deploy-roots.txt` 时逐根逐文件 SHA256 比对；
   **v0.1.0 无部署根 → 输出 N/A 并留痕**（N/A 是显式状态，不是静默跳过）。
4. **④ 台账核对**：
   - **④a 机械断言**：CHANGELOG 最新条目文本中出现的每个 F-NN 必须已在台账登记，
     缺口 exit 3；
   - **④b 机械断言**：台账 F 编号按出现顺序单调不减、无重复；CHANGELOG 最新条目版本 ==
     frontmatter 版本。FAIL → exit 4；
   - 人工核验：台账处置行的"措施"须指名到文件与小节，runner 只管机械面。

exit code 约定：0=全绿；多类失败时取最小失败类编号（1<2<3<4）并在报告里列全。

## --self-test（反向实测，新指纹/新断言发布前必跑）

对**被保护的语义本体**做探针，不是对指纹串本身（改指纹串必 FAIL 是无信息量测试）：

- 探针 P1（逐条指纹）：把包复制到临时目录，对每条指纹在其锚文件中**单点删除**该语义串，
  在临时根上跑 ①，必须检出缺失——检出率 100% 才算指纹有效；
- 探针 P2（版本同步）：临时根上只改 SKILL.md 的 version，② 必须检出不一致；
- 探针 P3（台账缺口）：临时根上从台账删掉一个 CHANGELOG 引用的 F-NN，④a 必须检出 exit 3。

runner 首版先拿自己跑 --self-test（机器可检家族规矩：新工具先抓自己的 bug；首跑抓出
自己的 bug 是预期行为不是事故）。
