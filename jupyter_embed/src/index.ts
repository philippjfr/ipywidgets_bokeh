//import {output} from "@jupyter-widgets/jupyterlab-manager"
import * as base from "@jupyter-widgets/base"
import * as widgets from "@phosphor/widgets"
import * as controls from "@jupyter-widgets/controls"

//declare function define(pkg: string, mod: any): void
//
const d = (window as any).define

//d("@jupyter-widgets/output", [], output)
d("@jupyter-widgets/base", [], base)
d("@phosphor/widgets", [], widgets)
d("@jupyter-widgets/controls", [], controls)

export {WidgetManager} from "./manager"
