# Lowest-cost cluster profile. Hand this to the accelerator:
#   lakebase deploy code_migration --vars <this-file>
# Single driver-only node, spot, fast idle shutdown. Fine for the small sample.
usecase                 = "code_migration"
cloud                   = "azure"
spark_version           = "15.4.x-scala2.12"
single_node             = true
use_spot                = true
autotermination_minutes = 10
