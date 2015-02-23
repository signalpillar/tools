# tools
Unsupported tools for interfacing with VirtualWisdom.

<h2>EntityImport.py</h2>

validates and imports entity import file to VW

Usage:  

  python3 EntityImport.py -v &lt;VW Appliance IP&gt; -u &lt;Username&gt; {-p &lt;Password&gt;|-z &lt;Password File&gt;} {-f &lt;Entity Import File&gt;|-i}

<h2>CSVNicknameToJSON.py</h2>

converts CSV WWN,nickname to entity import file

Usage:

  python3 CSVNicknameToJSON.py [-i &lt;Input File&gt;] [-o &lt;Output File&gt;]

<h2>CSVRelationsToJSON.py</h2>

converts CSV EntityType,EntityName,Members to entity import file

Usage:

  python3 CSVRelationsToJSON.py [-i &lt;Input File&gt;] [-o &lt;Output File&gt;]

<h2>ExportEntities.py</h2>

exports entity details to csv, by entity type or search by name

Usage:

  python3 ExportEntities.py -v &lt;VW Appliance IP&gt; -u &lt;Username&gt; {-p &lt;Password&gt;|-z &lt;Password File&gt;} {-e &lt;Entity Search String&gt;|-t &lt;Entity Type&gt;} [-o &lt;Output File&gt;] [--properties] [--exactonly]

<h2>ShowTopology.py</h2>

csv export of topology for a given entity name / entity id

Usage:

  python3 ShowTopology.py -v &lt;VW Appliance IP&gt; -u &lt;Username&gt; {-p &lt;Password&gt;|-z &lt;Password File&gt;} -e &lt;Entity Search String&gt; [-o &lt;Output File&gt;]

<h2>ExpandApplicationToInitiatorTarget.py</h2>

creates an application defined as Initiator:Target from an application defined as a set of hosts

Usage:

  python3 ExpandApplicationToInitiatorTarget.py -v &lt;VW Appliance IP&gt; -u &lt;Username&gt; {-p &lt;Password&gt;|-z &lt;Password File&gt;} {-a &lt;Application&gt;|-e &lt;Host&gt;[,&lt;Host&gt;][,&lt;Host&gt;]} [-o &lt;Output File&gt;]

| Notation | Description |
| -------- | ----------- |
| Text without brackets or braces | Items you must type as shown |
| &lt;Text inside angle brackets&gt; | Placeholder for which you must supply a value |
| [Text inside square brackets] | Optional items |
| {Text inside braces} | Set of required items; choose one |
| Vertical bar (&#124;) | Separator for mutually exclusive items; choose one |
| Ellipsis (...) | Items that can be repeated |
