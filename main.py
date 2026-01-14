import os
import re
import datetime
import sys
import json
import argparse
from rich.prompt import Prompt

# Import actions to ensure they register
import actions.web
import actions.filesystem
import actions.system
import actions.extended
import actions.internet
from actions import get_tools_schema, execute_action
from llm.engine import JarvisLLM
import ui

def save_report(content, user_prompt_snippet="report"):
    """Saves the content to a markdown file in reports/"""
    if not os.path.exists("reports"):
        os.makedirs("reports")
    
    # Sanitize filename
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    clean_snippet = re.sub(r'[^a-zA-Z0-9]', '_', user_prompt_snippet[:30])
    filename = f"reports/{timestamp}_{clean_snippet}.md"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# Report: {user_prompt_snippet}\n\n")
            f.write(f"**Date:** {datetime.datetime.now()}\n\n")
            f.write("---\n\n")
            f.write(content)
        ui.display_success(f"Compte rendu sauvegardé : {filename}")
    except Exception as e:
        ui.display_error(f"Erreur sauvegarde : {e}")

def main():
    parser = argparse.ArgumentParser(description="Jarvis AI Assistant")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode without loading the LLM.")
    args = parser.parse_args()

    ui.display_header()
    
    try:
        llm = JarvisLLM(mock=args.mock)
    except Exception as e:
        ui.display_error(f"Critical Error loading LLM: {e}")
        return

    tools_schema = get_tools_schema()
    
    ui.display_jarvis_message("Initialisation terminée. Je suis prêt. Comment puis-je vous aider ?")

    while True:
        try:
            user_input = Prompt.ask("\n[bold green]User[/bold green]")
            if not user_input:
                continue
            
            if user_input.lower() in ["exit", "quit", "q", "quitter"]:
                ui.display_jarvis_message("Au revoir.")
                break
            
            # === AGENTIC LOOP ===
            # We allow up to 25 steps for complex reasoning (User requested long horizon)
            current_input = user_input
            max_steps = 25
            
            for step in range(max_steps):
                # If step > 0, current_input is None (we rely on history)
                # We pass current_input only on the first iteration
                input_arg = current_input if step == 0 else None
                
                json_response_str = llm.generate_action(input_arg, tools_schema)
                
                try:
                    response_data = json.loads(json_response_str)
                    
                    thought = response_data.get("thought", "")
                    if thought:
                        ui.display_thought(thought)

                    msg_type = response_data.get("type", "chat")
                    content = response_data.get("content", "")

                    if msg_type == "action":
                        if isinstance(content, dict):
                            action_name = content.get("action_name")
                            action_args = content.get("args", {})
                            
                            ui.display_action(action_name, action_args)
                            
                            result = execute_action(action_name, action_args)
                            
                            # Show result, but do not stop. Feed it back.
                            result_msg = f"Action '{action_name}' completed. Result:\n{result}"
                            
                            if "Error" in str(result):
                                ui.display_error(str(result))
                            else:
                                ui.display_success("Action complétée. Analyse du résultat...")
                                
                            # Feed result back to memory using OBSERVATION keyword
                            # This strictly follows ReAct pattern so LLM knows it's the result of its action
                            llm.add_message("user", f"OBSERVATION: {result_msg}\n\n[SYSTEM]: Analyse cette observation. Si tu as la réponse, réponds avec type='chat'. Sinon, fais une autre action.")
                            
                            # Loop continues to next iteration to let LLM react to result
                            continue
                            
                        else:
                            ui.display_error(f"Invalid action format: {content}")
                            break # Break loop on error

                    else: # msg_type == "chat"
                        ui.display_jarvis_message(content)
                        # AUTO SAVE REPORT
                        save_report(content, user_prompt_snippet=user_input)
                        break # Done, return to user input
                    
                except json.JSONDecodeError:
                    ui.display_error(f"Failed to parse JSON: {json_response_str}")
                    break
                except Exception as e:
                    ui.display_error(f"Error processing response: {e}")
                    break
            else:
                ui.display_warning("Limite de réflexion atteinte. Synthèse forcée...")
                # Force final response
                llm.add_message("user", "[SYSTEM]: STOP. Arrête de chercher. GÉNÈRE MAINTENANT ta réponse finale au format JSON {type: 'chat', content: '...'} avec tout ce que tu sais. Tu DOIS répondre.")
                
                # One last generation for the forced answer
                json_response_str = llm.generate_action(None, tools_schema)
                try:
                    response_data = json.loads(json_response_str)
                    content = response_data.get("content", "")
                    
                    if response_data.get("type") == "action":
                         # Fallback: if it tries to act again, just take the thought or content string representation
                         final_text = response_data.get("thought", "Impossible de synthétiser (Action Loop).")
                         ui.display_jarvis_message(final_text)
                         save_report(final_text, user_prompt_snippet=user_input)
                    else:
                         ui.display_jarvis_message(content)
                         save_report(content, user_prompt_snippet=user_input)
                         
                except json.JSONDecodeError:
                    # Fallback for raw text response (sometimes LLM panics and gives raw Markdown)
                    ui.display_warning("Réponse malformée (JSON), affichage brut :")
                    ui.display_jarvis_message(json_response_str)
                    save_report(json_response_str, user_prompt_snippet=user_input)
                except Exception as e:
                    ui.display_error(f"Erreur critique lors de la synthèse : {e}")

        except KeyboardInterrupt:
            print("\n")
            ui.display_jarvis_message("Arrêt d'urgence. Au revoir.")
            break

if __name__ == "__main__":
    main()
