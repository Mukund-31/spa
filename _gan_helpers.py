                        print(f"{Fore.GREEN}✅ ATTACK SUCCESSFUL (Evaded Detection){Style.RESET_ALL}")
                        print(f"  Final Score: {decision.final_score:.1f}%")
                        print(f"  Confidence: {confidence:.1f}%\n")
                        
                        # Detector learns from failure
                        detector_learning = f"Missed attack: {num_txns} txns with progressive amounts - need better pattern detection"
                        detector_learnings.append(detector_learning)
                        
                        print(f"{Fore.YELLOW}📚 Detector Learning:{Style.RESET_ALL}")
                        print(f"  {detector_learning}\n")
                    
                    # Store learnings in Kafka
                    self._publish_learning_feedback(round_num, fraudster_learnings, detector_learnings, decision)
                else:
                    # Just update streaming context for intermediate transactions
                    self.coordinator.streaming_engine.update_context(tx.__dict__)
        
        # Final summary
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"🏁 GAN TRAINING SUMMARY")
        print(f"{'='*80}{Style.RESET_ALL}\n")
        
        print(f"{Fore.RED}Fraudster Learnings ({len(fraudster_learnings)} total):{Style.RESET_ALL}")
        for i, learning in enumerate(fraudster_learnings, 1):
            print(f"  {i}. {learning}")
        
        print(f"\n{Fore.GREEN}Detector Learnings ({len(detector_learnings)} total):{Style.RESET_ALL}")
        for i, learning in enumerate(detector_learnings, 1):
            print(f"  {i}. {learning}")
        
        print(f"\n{Fore.YELLOW}💡 Both systems are now smarter!{Style.RESET_ALL}\n")
    
    def _extract_fraudster_learning(self, decision, amounts, num_txns):
        """Extract what fraudster should learn from detection"""
        learnings = []
        
        if decision.final_score > 80:
            learnings.append("reduce transaction velocity")
        if num_txns > 5:
            learnings.append("use fewer transactions")
        if max(amounts) / min(amounts) > 3:
            learnings.append("make amounts less progressive")
        
        if not learnings:
            learnings.append("use different merchant categories")
        
        return ", ".join(learnings)
    
    def _publish_learning_feedback(self, round_num, fraudster_learnings, detector_learnings, decision):
        """Publish learnings to Kafka analysis-feedback topic"""
        feedback = {
            "round": round_num,
            "timestamp": datetime.now().isoformat(),
            "fraudster_learnings": fraudster_learnings,
            "detector_learnings": detector_learnings,
            "decision": {
                "final_score": decision.final_score,
                "decision": decision.decision
            }
        }
        
        try:
            self.producer.send(
                'analysis-feedback',
                value=feedback
            )
            self.producer.flush()
        except Exception as e:
            print(f"{Fore.YELLOW}Note: Could not publish to Kafka (is it running?): {e}{Style.RESET_ALL}")
