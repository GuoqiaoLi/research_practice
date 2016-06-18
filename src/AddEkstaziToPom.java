import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import org.w3c.dom.Document;
import org.w3c.dom.NodeList;
import org.w3c.dom.Node;
import org.w3c.dom.Element;
import java.io.File;

public class AddEkstaziToPom {

	public static Node createBuild(Document doc){
		Element build = doc.createElement("build");
		return build;
	}

	public static Node createPlugins(Document doc){
		Element plugins = doc.createElement("plugins");
		plugins.appendChild(createPlugin(doc));
		return plugins;
	}

	public static Node createPlugin(Document doc){
		Element plugin = doc.createElement("plugin");
		plugin.appendChild(createEkstaziElement(doc, "groupId", "org.ekstazi"));
		plugin.appendChild(createEkstaziElement(doc, "artifactId", "ekstazi-maven-plugin"));
		plugin.appendChild(createEkstaziElement(doc, "version", "4.6.1"));
		plugin.appendChild(createExecutions(doc));

		return plugin;
	}

	public static Node createExecutions(Document doc){
		Element executions = doc.createElement("executions");
		executions.appendChild(createExecution(doc));

		return executions;
	}

	public static Node createExecution(Document doc){
		Element execution = doc.createElement("execution");
		execution.appendChild(createEkstaziElement(doc, "id", "ekstazi"));
		execution.appendChild(createGoals(doc));

		return execution;
	}

	public static Node createGoals(Document doc){
		Element goals = doc.createElement("goals");
		goals.appendChild(createEkstaziElement(doc, "goal", "select"));

		return goals;
	}

	public static Node createEkstaziElement(Document doc, String name, String value){
		Element element = doc.createElement(name);
		element.appendChild(doc.createTextNode(value));
		return element;
	}


	public static void main(String argv[]) {
		for (int i = 0; i < argv.length; i++){
			String pomPath = argv[i];

			try{
				File xmlFile = new File(pomPath);
				DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
				DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
				Document doc = dBuilder.parse(xmlFile);

				Element root = doc.getDocumentElement();
				Boolean tagBuild = false;
				Element build = null;
				Node child = root.getFirstChild();
				while (child.getNextSibling() != null){
					if(child.getNodeName() == "build"){
						build = (Element)child;
						tagBuild = true;
					}

					child = child.getNextSibling();
				}

				if(build == null){
					build = (Element) createBuild(doc);
					root.appendChild(build);
				}

				// find plugins tag
				Boolean tagPlugins = false;
				child = build.getFirstChild();
				while(child != null && child.getNextSibling() != null){
					// System.out.println(child.getNodeName());
					if (child.getNodeName() == "plugins"){
						Element plugins = (Element) child;
						plugins.appendChild(createPlugin(doc));
						tagPlugins = true;
					}

					child = child.getNextSibling();
				}

				// plugins not find, add plugins to build
				if(!tagPlugins){
					build.appendChild(createPlugins(doc));
				}

				// write to pom.xml
				TransformerFactory transformerFactory = TransformerFactory.newInstance();
		        Transformer transformer = transformerFactory.newTransformer();
		        DOMSource source = new DOMSource(doc);
		        StreamResult result = new StreamResult(new File(pomPath));
		        transformer.transform(source, result);

			}
			catch(Exception e){
				e.printStackTrace();
			}
		}
	}

}